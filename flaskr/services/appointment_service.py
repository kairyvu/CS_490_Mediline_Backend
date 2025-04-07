from datetime import datetime
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

def add_appointment(doctor_id, patient_id, treatment, start_date, end_date=None):
    appointment_detail = AppointmentDetail(
        treatment=treatment,
        start_date=start_date,
        end_date=end_date,
        status=AppointmentStatus.PENDING
    )
    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        appointment_detail=appointment_detail
    )
    db.session.add(appointment)
    db.session.commit()

def update_appointment(appointment_id, treatment, start_date):
    appointment_detail = AppointmentDetail.query.get(appointment_id)
    if not appointment_detail:
        raise ValueError("Appointment not found")
    if appointment_detail.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
        raise ValueError("Only appointments with pending or confirmed status can be updated")
    if not treatment or not start_date:
        raise ValueError("treatment and start_date are required")
    
    appointment_detail.treatment = treatment
    current_dt = datetime.now()
    if start_date < current_dt:
        raise ValueError("start_date cannot be before the current date")
    appointment_detail.start_date = start_date
    appointment_detail.end_date = None
    appointment_detail.status = AppointmentStatus.PENDING
    db.session.commit()