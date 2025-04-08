from flaskr.models import Doctor
from flaskr.extensions import db

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

