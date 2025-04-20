import re
from werkzeug.datastructures import ImmutableMultiDict
from flaskr.models import Patient, Doctor
from flaskr.extensions import db
from .forms import UserRegistrationForm

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

def update_patient(user_id, updates: dict) -> dict:
    patient: Patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return {"error": "Patient not found"}

    pat_attr = {at for at in dir(patient) 
                if not (re.match(r'__.*__', at) or re.match(r'_sa.*', at))}
    if not (set(updates) <= pat_attr):
        return {"message": "no updates performed"}

    # Do validation on updates
    updates.update({
        'username': patient.user.username,
        'password': patient.user.password,
        'account_type': 'patient'
    })

    if "first_name" not in updates:
        updates.update({"first_name": patient.first_name})

    if "last_name" not in updates:
        updates.update({"last_name": patient.last_name})

    if "email" not in updates:
        updates.update({"email": patient.email})

    if "phone" not in updates:
        updates.update({"phone": patient.phone})

    if "address1" not in updates:
        updates.update({"address1": patient.user.address.address1})

    if "city" not in updates:
        updates.update({"city": patient.user.address.city})

    if "state" not in updates:
        updates.update({"state": patient.user.address.state})

    if "country" not in updates:
        updates.update({"country": patient.user.address.city.country})

    if "zipcode" not in updates:
        updates.update({"zipcode": patient.user.address.zipcode})
    
    updates_form = ImmutableMultiDict(list(updates.items()))
    updates_check = UserRegistrationForm(updates_form)
    if not updates_check.validate():
        m = list(updates_check.errors.items())
        m2 = [{it[0]: it[1][0]} for it in m]
        return {'error': m2}
    patient.first_name = updates['first_name']
    patient.last_name = updates['last_name']
    patient.email = updates['email']
    patient.phone = updates['phone']

    db.session.commit()
    return {"message": "Patient updated successfully"}