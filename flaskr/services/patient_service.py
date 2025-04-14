from flaskr.models import Patient, Doctor
from flaskr.extensions import db

def get_patient_info(user_id):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return None

    doctor = Doctor.query.filter_by(user_id=patient.doctor_id).first()

    return {
        "user_id": patient.user_id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "email": patient.email,
        "phone": patient.phone,
        "dob": str(patient.dob),
        "doctor": {
            "user_id": doctor.user_id,
            "first_name": doctor.first_name,
            "last_name": doctor.last_name,
            "specialization": doctor.specialization,
            "fee" : doctor.fee
        } if doctor else None
    }

def update_patient(user_id, updates):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return None

    if "first_name" in updates:
        patient.first_name = updates["first_name"]

    if "last_name" in updates:
        patient.last_name = updates["last_name"]

    if "email" in updates:
        patient.email = updates["email"]

    if "phone" in updates:
        patient.phone = updates["phone"]

    db.session.commit()
    return {"message": "Patient updated successfully"}