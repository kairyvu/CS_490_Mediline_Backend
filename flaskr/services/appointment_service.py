from datetime import datetime
from flask_jwt_extended.exceptions import NoAuthorizationError
from flaskr.extensions import db
from flaskr.struct import AppointmentStatus
from flaskr.models.appointment import Appointment, AppointmentDetail
from flaskr.models import User, Patient, Doctor

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
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
    
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
    # Get the newly made appointment's ID
    db.session.flush()
    appointment_detail.appointment_details_id = appointment.appointment_id
    db.session.commit()
    return appointment.appointment_id

def update_appointment(appointment_id, treatment, start_date, 
                       status=AppointmentStatus.PENDING, end_date=None, 
                       requesting_user: User|None=None):
    if not requesting_user:
        raise NoAuthorizationError
    appointment_detail = AppointmentDetail.query.get(appointment_id)
    if not appointment_detail:
        raise ValueError("Appointment not found")
    _appt_dr = appointment_detail.appointment.doctor_id
    _appt_pt = appointment_detail.appointment.patient_id
    if (requesting_user.user_id not in {_appt_dr, _appt_pt}
        and requesting_user.account_type.name != 'SuperUser'):
        raise NoAuthorizationError
    if appointment_detail.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
        raise ValueError("Only appointments with PENDING or CONFIRMED status can be updated")
    if status and not hasattr(AppointmentStatus, status):
        raise ValueError(f"Invalid status value: {status}")
    if isinstance(start_date, str):
        try:
            start_date = datetime.fromisoformat(start_date)
        except Exception as e:
            raise ValueError("Invalid start_date format") from e
        # No end date supplied; check newly submitted start date is before
        # previously submitted end date
        if (appointment_detail.end_date != None) and (appointment_detail.end_date <= start_date):
            raise ValueError(f"end_date {appointment_detail.end_date} " +
                             f"must be after start_date {start_date}")
        
    if end_date and isinstance(end_date, str):
        try:
            end_date = datetime.fromisoformat(end_date)
        except Exception as e:
            raise ValueError("Invalid end_date format") from e
        if end_date <= start_date:
            raise ValueError(f"end_date {end_date} " + 
                             f"must be after start_date {start_date}")
        else:
            if appointment_detail.end_date != end_date:
                appointment_detail.end_date = end_date

    # TODO: This code could be written way better but im lazy and pushing quick fixes
    if appointment_detail.treatment != treatment:
        appointment_detail.treatment = treatment
    if appointment_detail.start_date != start_date:
        appointment_detail.start_date = start_date
    if appointment_detail.status != status:
        appointment_detail.status = status
    db.session.commit()
    return

def get_appointment(appointment_id):
    appointment_detail = AppointmentDetail.query.get(appointment_id)
    if not appointment_detail:
        raise ValueError("Appointment not found")
    return appointment_detail.to_dict()