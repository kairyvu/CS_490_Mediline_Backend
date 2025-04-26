#from flask import current_app
from celery import current_app
from celery.result import AsyncResult
from flaskr.models import Prescription, Patient, PrescriptionMedication, Medication
from flaskr.struct import PrescriptionStatus
from flaskr.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func

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

def add_pt_rx(pharmacy_id, patient_id, doctor_id, medications):
    # TODO: detect duplicates
    try:
        res: AsyncResult = current_app.send_task(
                'celery_utils.tasks.process_rx', 
                args=(pharmacy_id, patient_id, doctor_id, medications),
                queue='prescription_queue'
            )
    except Exception as e:
        raise e
    return res.status

def old_add_pt_rx(pharmacy_id, patient_id, doctor_id, medications):
    # 1) create entry in prescription table
    new_rx = Prescription(
        patient_id=patient_id,
        doctor_id=doctor_id,
        pharmacy_id=pharmacy_id,
        amount=0,
        status=PrescriptionStatus.UNPAID
    )
    db.session.add(new_rx)
    # Flush to get new prescription id
    try:
        db.session.flush()
    except Exception as e:
        raise e
    # 2) for each medication, create entry in rx-med table
    for med in medications:
        new_pt_rx_request = PrescriptionMedication(
            prescription_id=new_rx.prescription_id,
            medication_id=med['medication_id'],
            dosage=med['dosage'],
            medical_instructions=med['instructions'],
            taken_date=datetime.now(),      # what is this supposed to be?
            duration=20
        )
        db.session.add(new_pt_rx_request)
        try:
            db.session.flush()
        except Exception as e:
            raise e
    try:
        db.session.commit()
    except Exception as e:
        raise e
    return new_rx.prescription_id
    