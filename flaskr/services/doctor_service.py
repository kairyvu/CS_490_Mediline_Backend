from flaskr.models import Doctor, Patient, Appointment, AppointmentDetail, RatingSurvey, Chat, Message
from flaskr.extensions import db
from datetime import date, datetime

def all_doctors(sort_by='user_id', order='asc'):
    if not hasattr(Doctor, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    column = getattr(Doctor, sort_by)

    if order == 'desc':
        column = column.desc()

    doctors = (
        Doctor.query
        .with_entities(
            Doctor.user_id,
            Doctor.first_name,
            Doctor.last_name,
            Doctor.specialization
        )
        .order_by(column)
        .all()
    )
    return [
        {
            "user_id": doc.user_id,
            "name": f"{doc.first_name} {doc.last_name}",
            "specialization": doc.specialization
        }
        for doc in doctors
    ]

def doctor_details(doctor_id):
    doctor = Doctor.query.filter_by(user_id=doctor_id).first()
    if not doctor:
        return None

    return doctor.to_dict()

def total_patients(doctor_id):
    return Patient.query.filter_by(doctor_id=doctor_id).count()
def upcoming_appointments_count(doctor_id):
    upcoming_count = Appointment.query.filter_by(doctor_id=doctor_id).join(AppointmentDetail).filter(AppointmentDetail.status == "CONFIRMED").count()
    return (upcoming_count)
def pending_appointments_count(doctor_id):
    pending_count = Appointment.query.filter_by(doctor_id=doctor_id).join(AppointmentDetail).filter(AppointmentDetail.status == "PENDING").count()
    return (pending_count)
def doctor_patients_count(doctor_id):
    patients_count = Patient.query.filter_by(doctor_id=doctor_id).count()
    return (patients_count)
def todays_patient(doctor_id, date):
    try:
        query_date = datetime.strptime(date, '%Y-%m-%d').date() if date else datetime.today().date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}
    appointments = Appointment.query \
        .filter_by(doctor_id=doctor_id) \
        .join(AppointmentDetail) \
        .filter(db.func.date(AppointmentDetail.start_date) == query_date) \
        .all()
    result = []
    for app in appointments:
        patient = Patient.query.filter_by(user_id=app.patient_id).first()
        detail = app.appointment_detail

        if patient:
            result.append({
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "visit_time": detail.start_date.strftime("%I:%M %p"),
                "dob": patient.dob,
                "treatment": detail.treatment,
                "status": detail.status.name,
                "email": patient.email,
                "phone_number": patient.phone
            })
    return result

def doctor_rating_detail(doctor_id, sort_by='stars', order='desc'):
    query  = RatingSurvey.query.filter_by(doctor_id=doctor_id)

    column = getattr(RatingSurvey, sort_by)
    if order == 'desc':
        column = column.desc()
    query = query.order_by(column)
    ratings = query.all()
    if not ratings:
        return{
            "average_rating": 0,
            "ratings": []
        }
    
    total_stars = sum(rate.stars for rate in ratings)
    avg_rating = round(total_stars/len(ratings), 2)

    rating_detail = []
    for rate in ratings:
        patient = Patient.query.filter_by(user_id=rate.patient_id).first()
        rating_detail.append({
            "patient_id": rate.patient_id,
            "patient_name": f"{patient.first_name} {patient.last_name}",
            "stars":rate.stars,
            "comment": rate.comment
        })

    return {
        "average_rating": avg_rating,
        "ratings": rating_detail
    }

def last_completed_appointment(patient_id, doctor_id):
    appointment = Appointment.query \
        .filter_by(patient_id=patient_id, doctor_id=doctor_id) \
        .join(AppointmentDetail) \
        .filter(AppointmentDetail.status == 'completed') \
        .order_by(AppointmentDetail.end_date.desc()) \
        .first()
    if not appointment:
        return {"message": "No Comleted Appointment Found"}
    patient = Patient.query.filter_by(user_id= patient_id).first()
    today = date.today()
    age = today.year - patient.dob.year

    return {
        "appintment_id": appointment.appointment_id,
        "end_date": str(appointment.appointment_detail.end_date),
        "patient_info":{
            "dob": patient.dob,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "age": age,
            "phone": patient.phone
        }
    }

def doctor_general_discussion(doctor_id):
    doctor = Doctor.query.filter_by(user_id=doctor_id).first()
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    result = []

    for appt in appointments:
        patient = Patient.query.filter_by(user_id=appt.patient_id).first()
        chat = Chat.query.filter_by(appointment_id=appt.appointment_id).first()
        if not chat or not patient:
            continue
        messages = Message.query.filter_by(chat_id=chat.chat_id).all()
        for msg in messages:
            if msg.user_id == doctor_id:
                sender_name = f"{doctor.first_name} {doctor.last_name}"
            else:
                sender_name = f"{patient.first_name} {patient.last_name}"

            result.append({
                "chat_id": chat.chat_id,
                "sender_name": sender_name,
                "message": msg.message_content,
                "timestamp": msg.time.strftime("%Y-%m-%d %I:%M %p")
            })
    return result

def select_doctor(doctor_id, patient_id):
    # Creates relationship between doctor and patient
    pt: Patient = Patient.query.filter_by(user_id=patient_id).first()
    if not pt:
        raise ValueError(f'patient with id {patient_id} not found')
    
    dr: Doctor = Doctor.query.filter_by(user_id=doctor_id).first()
    if not dr: 
        raise ValueError(f'doctor with id {doctor_id} not found')
    
    pt.doctor_id = doctor_id
    pt.doctor = dr
    # Don't worry about doctor accepting patient requests yet;
    # Automatically append pt to doctor's patients list
    dr.patients.append(pt)
    db.session.add_all((pt, dr))
    try:
        db.session.commit()
    except Exception as e:
        raise e

    return
