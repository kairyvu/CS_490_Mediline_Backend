from datetime import datetime, timedelta
from sqlalchemy import func
from celery import shared_task

from flaskr.models import Prescription, Patient
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

### PHARMACY TASKS
@shared_task(ignore_result=False)
def add_together(a: int, b: int) -> int:
    return a + b