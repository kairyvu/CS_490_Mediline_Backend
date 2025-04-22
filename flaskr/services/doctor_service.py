from flaskr.models import Doctor, Patient, Appointment, AppointmentDetail, RatingSurvey, Chat, Message
from flaskr.extensions import db
from datetime import date

def all_doctors():
    doctors = Doctor.query.with_entities(
        Doctor.user_id,
        Doctor.first_name,
        Doctor.last_name,
        Doctor.specialization
    ).all()

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

    return {
        "user_id": doctor.user_id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "email": doctor.email,
        "phone": doctor.phone,
        "specialization": doctor.specialization,
        "bio": doctor.bio,
        "fee": doctor.fee,
        "profile_picture": doctor.profile_picture,
        "dob": doctor.dob.strftime('%Y-%m-%d') if doctor.dob else None,
        "license_id": doctor.license_id,
    }

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
def todays_patient(doctor_id):
    today = date.today()
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).join(AppointmentDetail).filter(db.func.date(AppointmentDetail.start_date) == today).all()
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
                "statues": detail.status.name,
                "email": patient.email,
                "phone_number": patient.phone

            })

    return result
def doctor_rating_detail(doctor_id, sort_by='stars', order='desc'):
    query  = RatingSurvey.query.filter_by(doctor_id =doctor_id)

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
    appointment = Appointment.query.filter_by(patient_id=patient_id, doctor_id=doctor_id).join(AppointmentDetail).filter(AppointmentDetail.status == 'completed').order_by(AppointmentDetail.end_date.desc()).first()
    if not appointment:
        return {"message": "No Comleted Appointment Found"}
    patient = Patient.query.filter_by(user_id= patient_id).first()
    today = date.today()
    age = today.year - patient.dob.year

    return {
        "appintment_id": appointment.appointment_id,
        "end_date": str(appointment.appointment_detail.end_date),
        "patient_info":{
            "dob" : patient.dob,
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