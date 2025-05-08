from datetime import datetime, timedelta
from sqlalchemy import func
from flask import jsonify, Response

from flaskr.models import Prescription, Patient, Pharmacy
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
    
    med_schema = {'dosage', 'instructions', 'medication_id'}
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

def add_pt_rx(pharmacy_id, patient_id, doctor_id, medications): # TODO - need to do with RabbitMQ
    pass

def get_pharmacy_info(pharmacy_id):
    pharmacy = Pharmacy.query.filter_by(user_id=pharmacy_id).first()
    if not pharmacy:
        return None

    return pharmacy.to_dict()
