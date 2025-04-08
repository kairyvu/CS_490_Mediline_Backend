from flaskr.models import Patient, Doctor, Invoice, Appointment, AppointmentDetail
from flaskr.extensions import db
from datetime import datetime

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



def get_invoices_by_patient(user_id):
    invoices = Invoice.query.filter_by(patient_id=user_id).order_by(Invoice.pay_date.desc()).all()
    return [
        {
            "invoice_id": i.invoice_id,
            "status": i.status.value,
            "pay_date": i.pay_date.strftime("%Y-%m-%d"),
            "created_at": i.created_at.strftime("%Y-%m-%d"),
            "doctor_id": i.doctor_id
        } for i in invoices
    ]




def upcoming_appointments(user_id):
    appointments = (

        db.session.query(Appointment)
        .join(AppointmentDetail)
        .filter(Appointment.patient_id == user_id)
        .filter(AppointmentDetail.status == "PENDING")
        .order_by(AppointmentDetail.start_date.asc())
        .all()
    )

    result = []
    for appt in appointments:
        detail = appt.appointment_detail
        doctor = appt.doctor

        result.append({
            "appointment_id": appt.appointment_id,
            "doctor": {
                "user_id": doctor.user_id,
                "first_name": doctor.first_name,
                "last_name": doctor.last_name,
                "specialization": doctor.specialization
            },
            "start_date": detail.start_date,
            "status": detail.status.value
        })

    return result




def create_appointment(data):
    new_appt = Appointment(
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.session.add(new_appt)
    db.session.commit()

    start = datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M")
    end = datetime.strptime(data["end_time"], "%Y-%m-%d %H:%M")
    
    new_detail = AppointmentDetail(
        appointment_details_id=new_appt.appointment_id,
        start_date=start,
        end_date=end,
        status= "PENDING"
    )
    db.session.add(new_detail)
    db.session.commit()

    return {"message": "Appointment created"}



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




