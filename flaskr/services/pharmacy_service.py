import json
from datetime import datetime, timedelta
from sqlalchemy import func
from flask import jsonify, Response

from flaskr.struct import PrescriptionStatus
from flaskr.models import Prescription, PrescriptionMedication, Patient, Pharmacy, User, Notification
from flaskr.extensions import db

def get_all_pharmacy_patients(pharmacy_id, new_request_time=datetime.now() - timedelta(hours=24)):
    rows = (
        db.session.query(
            Patient.user_id,
            Patient.first_name,
            Patient.last_name,
            func.max(Prescription.created_at).label("last_prescribed")
        ).join(Prescription, Prescription.patient_id == Patient.user_id)
        .filter(Prescription.pharmacy_id == pharmacy_id)
        .group_by(Patient.user_id, Patient.first_name, Patient.last_name)
        .all()
    )

    new_patients = []
    other_patients = []
    for id, first_name, last_name, created_at in rows:
        obj = {
            'patient_id':   id,
            'patient_name': f"{first_name} {last_name}"
        }
        if created_at >= new_request_time:
            new_patients.append(obj)
        else:
            other_patients.append(obj)

    return {
        'new_patients':   new_patients,
        'other_patients': other_patients
    }

def validate_rx(data: dict) -> Response|tuple[int, int, list]:
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    med_schema = {'dosage', 'instructions', 'medication_id', 'taken_date', 'duration'}
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    medications = data.get('medications')

    # perform validation
    if not all([patient_id, doctor_id, medications]):
        return jsonify(error='missing required fields'), 400
    if len(medications) == 0:
        return jsonify(error='no medications in prescription'), 400
    if not all([isinstance(med, dict) for med in medications]):
        return jsonify(error='medications must be json objects'), 400
    for med in medications:
        schema_diff = set(med) - med_schema
        if schema_diff:
            return jsonify({
                'error': "schema doesn't conform",
                'invalid': list(schema_diff)
            }), 400
        if not all([attr in med_schema for attr in med]):
            return jsonify({
                'error': f'medication {med} has missing attributes'
            }), 400
    return patient_id, doctor_id, medications

# Helper to ensure doctor sending the rx is allowed to
def check_rx_auth(patient_id, doctor_id, pharmacy_id, requesting_user) -> bool:
    _u: User = requesting_user
    pt: User = User.query.filter_by(user_id=patient_id).first()
    if _u.account_type.name == 'SuperUser':
        return True
    if _u.user_id != doctor_id:
        return False
    if pt.patient.doctor_id != doctor_id:
        return False
    if pt.patient.pharmacy_id != pharmacy_id:
        return False
    return True 


def add_pt_rx(pharmacy_id, patient_id, doctor_id, medications):
    import os
    import json
    payload = {
        "pharmacy_id": pharmacy_id,
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "medications": medications
    }
    if os.environ.get('FLASK_ENV') == 'development': 
        from flaskr.models import Notification
        # create a notification
        n = Notification(
            user_id=pharmacy_id,
            notification_content=json.dumps(payload, default=str)
        )
        db.session.add(n)
        try:
            db.session.commit()
        except Exception as e:
            raise e
        return n.notification_id
    else:
        from google.cloud.pubsub_v1 import PublisherClient
        from google.api_core.exceptions import NotFound

        publisher = PublisherClient()
        topic_path = publisher.topic_path(
            os.environ.get('GCLOUD_PROJECT_ID'),
            os.environ.get('GCLOUD_TOPIC_ID'))

        try:
            data_str = json.dumps(payload, default=str)
            data = data_str.encode('utf-8')
            future = publisher.publish(topic_path, data)
            return future
        except NotFound as e:
            raise e
        except Exception as e:
            raise e

def get_pharmacy_info(pharmacy_id):
    pharmacy = Pharmacy.query.filter_by(user_id=pharmacy_id).first()
    if not pharmacy:
        return None

    return pharmacy.to_dict()

def fetch_rx_requests(pharmacy_id):
    requests: list[Notification] = Notification.query.filter_by(user_id=pharmacy_id).all()
    rtn = []
    for r in requests:
        res = {}
        try:
            content = json.loads(r.notification_content)
        except Exception as e:
            raise e
        res = r.to_dict()
        res['created_at'] = r.created_at.isoformat()
        res['notification_content'] = content
        rtn.append(res)

    return rtn

# internal use
def accept_prescription(pharmacy_id, rx_str):
    try:
        rx = json.loads(rx_str)
    except:
        raise ValueError('invalid prescription')
    prices = dict()
    for m in (ms := rx['medications']):
        units = m['dosage'] # Treat dosage as item units
        price = (int((m_id := m['medication_id'])) % 20) + 20 # Generate a random & deterministic price
        if m_id not in prices:
            prices[m_id] = price * units
        else:
            prices[m_id] += price * units
    amount = sum(list(prices.values()))

    new_rx = Prescription(
        patient_id=rx['patient_id'],
        doctor_id=rx['doctor_id'],
        pharmacy_id=rx['pharmacy_id'],
        amount=amount,
        status=PrescriptionStatus.UNPAID
    )
    db.session.add(new_rx)
    try:
        db.session.flush()
    except Exception as e:
        raise e

    for m in ms:
        new_rx_med = PrescriptionMedication(
            prescription_id=new_rx.prescription_id,
            medication_id=m['medication_id'],
            dosage=m['dosage'],
            medical_instructions=m['instructions'],
            taken_date=m['taken_date'],
            duration=m['duration']
        )
        db.session.add(new_rx_med)
        try:
            db.session.flush()
        except Exception as e:
            raise e
    try:
        db.session.commit()
    except Exception as e:
        raise e
    return new_rx.prescription_id
    
def handle_rx_request(pharmacy_id, rx_id, status):
    request: Notification = Notification.query.filter_by(notification_id=rx_id).first()
    if not request:
        raise ValueError('request not found')
    did_accept = status == 'accepted'
    if did_accept:
        id = accept_prescription(pharmacy_id, request.notification_content)
    db.session.delete(request)
    db.session.commit()
    if did_accept:
        return id
    return None

def validate_body(body: dict) -> tuple[bool, Response] | tuple[int, str]:
    if 'notification_id' not in body:
        return jsonify({'error': 'request body must include notification_id'})
    if not isinstance(body['notification_id'], int):
        return jsonify({'error': 'notification_id must be int'})
    if 'status' not in body:
        return jsonify({'error': 'request body must include status'})
    if body['status'] not in ['accepted', 'rejected']:
        return jsonify({'error': "status must be 'accepted' or 'rejected'"})
    return body['notification_id'], body['status']