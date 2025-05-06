from flaskr.models import MedicalRecord, Doctor, Patient
from flaskr.extensions import db

def get_medical_records_by_user(user_id, sort_by='created_at', order='desc'):
    is_patient = Patient.query.get(user_id) is not None
    is_doctor = Doctor.query.get(user_id) is not None
    if not (is_patient or is_doctor):
        raise ValueError("User not found as either patient or doctor")
    query = MedicalRecord.query
    if is_patient:
        query = query.filter(MedicalRecord.appointment.has(patient_id=user_id))
    elif is_doctor:
        query = query.filter(MedicalRecord.appointment.has(doctor_id=user_id))
    if not hasattr(MedicalRecord, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    column = getattr(MedicalRecord, sort_by)
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
    query = query.order_by(column)
    medical_records = query.all()
    return [record.to_dict() for record in medical_records]