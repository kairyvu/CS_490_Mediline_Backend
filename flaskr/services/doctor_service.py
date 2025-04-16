from flaskr.models import Doctor, Patient, Appointment, AppointmentDetail
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
                "visit_time": detail.start_date.strftime("%I:%M %p") 
            })

    return result
