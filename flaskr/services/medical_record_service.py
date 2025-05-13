from flaskr.models import MedicalRecord, Doctor, Patient, User, Appointment
from flaskr.extensions import db
from datetime import datetime


def get_medical_records_by_user(user_id, sort_by='created_at', order='desc', requesting_user: User|None=None):
    from flaskr.services import UnauthorizedError
    is_patient = Patient.query.get(user_id) is not None
    is_doctor = Doctor.query.get(user_id) is not None
    if not (is_patient or is_doctor):
        raise ValueError("User not found as either patient or doctor")

    query = MedicalRecord.query
    if is_patient:
        query = query.filter(MedicalRecord.appointment.has(patient_id=user_id))
    elif is_doctor:
        query = query.filter(MedicalRecord.appointment.has(doctor_id=user_id))
    _id = requesting_user.user_id
    _is_su = requesting_user.account_type.name == 'SuperUser'
    _is_dr = requesting_user.account_type.name == 'Doctor'
    _is_pt = requesting_user.account_type.name == 'Patient'
    _dr_pts = None
    _pt_dr = None
    if _is_dr:
        _dr_pts = [p.user_id for p in requesting_user.doctor.patients]
    if ((is_patient) and not (_is_su or (_is_dr and (user_id in _dr_pts)) or (_is_pt and (_id == user_id)))):
        raise UnauthorizedError
    if ((is_doctor) and not (_is_su or (_is_dr and (user_id == _id)))):
        raise UnauthorizedError
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

def create_medical_record(appointment_id, patient_id, description):
    patient =Patient.query.filter_by(user_id = patient_id).first()
    appointment = Appointment.query.filter_by(appointment_id=appointment_id, patient_id=patient_id).first()
    if not appointment or not patient:
        return None

    record = MedicalRecord(
        appointment_id=appointment_id,
        description=description,
        created_at=datetime.now()
    )

    db.session.add(record)
    db.session.commit()

    return record.to_dict()


def update_medical_record(medical_record_id, description):
    record = MedicalRecord.query.get(medical_record_id)
    if not record:
        return None
    record.description = description
    db.session.commit()
    return record.to_dict()

def delete_medical_record(medical_record_id):
    record = MedicalRecord.query.get(medical_record_id)
    if not record:
        return None
    db.session.delete(record)
    db.session.commit()
    return {"message": "Medical record deleted successfully"}
