from flaskr.extensions import db
from flaskr.models.user import Doctor, Patient, Pharmacy
from . import get_patient_info, doctor_details, get_pharmacy_info

def get_user_info_by_id(user_id):
    is_patient = Patient.query.filter_by(user_id=user_id).first() is not None
    is_doctor = Doctor.query.filter_by(user_id=user_id).first() is not None
    is_pharmacy = Pharmacy.query.filter_by(user_id=user_id).first() is not None

    if not (is_patient or is_doctor or is_pharmacy):
        raise ValueError("User not found as either patient, doctor, or pharmacy")
    if is_patient:
        return get_patient_info(user_id)
    if is_doctor:
        return doctor_details(user_id)
    if is_pharmacy:
        return get_pharmacy_info(user_id)