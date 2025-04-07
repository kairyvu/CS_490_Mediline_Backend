from flaskr.extensions import db
from flaskr.struct import AppointmentStatus
from flaskr.models.appointment import Appointment, AppointmentDetail
from flaskr.models import Patient, Doctor

def get_upcoming_appointments(user_id, sort_by='start_date', order='desc'):
    is_patient = Patient.query.filter_by(user_id=user_id).first() is not None
    is_doctor = Doctor.query.filter_by(user_id=user_id).first() is not None
    
    if not (is_patient or is_doctor):
        raise ValueError("User not found as either patient or doctor")
    
    query = AppointmentDetail.query.join(Appointment)
    
    if is_patient:
        query = query.filter(Appointment.patient_id == user_id)
    elif is_doctor:
        query = query.filter(Appointment.doctor_id == user_id)
    
    query = query.filter(
        AppointmentDetail.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    )
    
    if not hasattr(AppointmentDetail, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    
    column = getattr(AppointmentDetail, sort_by)
    if order == 'desc':
        column = column.desc()
    
    query = query.order_by(column)
    appointments = query.all()
    
    return [ap.to_dict() for ap in appointments]