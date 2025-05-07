from datetime import date, datetime
from werkzeug.datastructures import ImmutableMultiDict
from flask import jsonify
from sqlalchemy import select, update
from sqlalchemy.exc import OperationalError, IntegrityError
from flask_jwt_extended.exceptions import NoAuthorizationError

from flaskr.models import User, Doctor, Patient, Appointment, AppointmentDetail, RatingSurvey, Chat, Message, City, Country, Address
from flaskr.extensions import db
from flaskr.struct import AppointmentStatus, Gender

from .forms import DrRegForm

def all_doctors(sort_by='user_id', order='asc'):
    if not hasattr(Doctor, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")
    column = getattr(Doctor, sort_by)
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")

    doctors = (
        Doctor.query
        .with_entities(
            Doctor.user_id,
            Doctor.first_name,
            Doctor.last_name,
            Doctor.specialization,
            Doctor.gender,
        )
        .order_by(column)
        .all()
    )
    return [
        {
            "user_id": doc.user_id,
            "name": f"{doc.first_name} {doc.last_name}",
            "specialization": doc.specialization,
            "gender": doc.gender.value if isinstance(doc.gender, Gender) else doc.gender,
        }
        for doc in doctors
    ]

def doctor_details(doctor_id):
    doctor = Doctor.query.filter_by(user_id=doctor_id).first()
    if not doctor:
        return None

    return doctor.to_dict()

def upcoming_appointments_count(doctor_id):
    upcoming_count = Appointment.query.filter_by(doctor_id=doctor_id).join(AppointmentDetail).filter(AppointmentDetail.status == "CONFIRMED").count()
    return (upcoming_count)
def pending_appointments_count(doctor_id):
    pending_count = Appointment.query.filter_by(doctor_id=doctor_id).join(AppointmentDetail).filter(AppointmentDetail.status == "PENDING").count()
    return (pending_count)
def doctor_patients_count_and_list(doctor_id):
    patients = Patient.query.filter_by(doctor_id=doctor_id).all()
    return {
        "doctor_patients_count": len(patients),
        "patients": [
            {
                "patient_id": patient.user_id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "email": patient.email,
                "dob": patient.dob,
                "phone": patient.phone,
                "gender": patient.gender.value
            }
            for patient in patients
        ]
    }

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
                "patient_id": patient.user_id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "gender": patient.gender.value if isinstance(patient.gender, Gender) else patient.gender,
                "visit_time": detail.start_date.isoformat(),
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
        return {"message": "No Completed Appointment Found"}
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
            "gender": patient.gender.value if isinstance(patient.gender, Gender) else patient.gender,
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

def new_appointments_request(doctor_id):
    appointments = (Appointment.query
        .filter_by(doctor_id=doctor_id)
        .join(AppointmentDetail, AppointmentDetail.appointment_details_id == Appointment.appointment_id)
        .filter(AppointmentDetail.status == AppointmentStatus.PENDING)
        .order_by(Appointment.created_at.desc())
        .all()
    )

    result = []
    for app in appointments:
        detail = app.appointment_detail
        result.append({
            "appointment_id": app.appointment_id,
            "patient_id": app.patient_id,
            "created_at": app.created_at.strftime("%Y-%m-%d %I:%M %p"),
            "status": detail.status.name,
            "visit_time": detail.start_date.strftime("%Y-%m-%d %I:%M %p")
        })

    return result

def update_doctor(user_id, updates: dict) -> dict:
    doctor: User = db.session.scalar(
        select(User)
        .where(User.user_id == user_id)
    )
    if not doctor.doctor:
        return {"error": "Doctor not found"}
    
    address_attr = {'address1', 'address2', 'state', 'zipcode'}
    doctor_attr = {'first_name', 'last_name', 'email', 'phone', 'dob', 
                   'specialization', 'fee', 'license_id', 'profile_picture', 
                   'bio', 'accepting_patients', 'gender'}

    invalid_attrs = set(updates) - (doctor_attr 
                                    | address_attr 
                                    | {'city', 'country'})
    if len(invalid_attrs) != 0: 
        return {
            "message": "no updates performed",
            "invalid_attributes": list(invalid_attrs)
        }

    curr_doctor_info = doctor.doctor.to_dict()
    # cast 'accepting_patients' in current doctor attribute
    # to string to allow comparison with updated value
    curr_doctor_info['accepting_patients'] = str(curr_doctor_info['accepting_patients'])
    curr_addr_info = doctor.address.to_dict()
    curr_city = db.session.scalar( 
        select(City)
        .where(City.city_id == doctor.address.city.city_id)
    )
    curr_country = db.session.scalar(
        select(Country)
        .where(Country.country_id == curr_city.country_id)
    )
    _city = {'city': updates.get('city') or curr_city.city}
    _country = {'country': updates.get('country') or curr_country.country}

    if isinstance(updates.get('accepting_patients'), bool):
        updates['accepting_patients'] = str(updates['accepting_patients'])
    elif isinstance(updates.get('accepting_patients'), str):
        if updates['accepting_patients']  == 'false':
            updates['accepting_patients'] = 'False'
        elif updates['accepting_patients'] == 'true':
            updates['accepting_patients'] = 'True'
        elif updates['accepting_patients'] in ['True', 'False']:
            pass
        else:
            raise Exception(f"updates['accepting_patients'] is {updates['accepting_patients']}")
    doctor_info_updates = {
        attr: 
            updates.get(attr) 
            or curr_doctor_info[attr] 
            for attr in doctor_attr
    }
    addr_info_updates = {
        attr: 
            updates.get(attr) 
            or curr_addr_info[attr] 
            for attr in address_attr
    }
    _updates = doctor_info_updates | addr_info_updates | _city | _country
    _updates.update({
        'username': doctor.username,
        'password': doctor.password,
        'account_type': 'doctor'
    })

    city_diff = curr_city.city != _city['city']
    country_diff = curr_country.country != _country['country']
    addr_diff = not all([ 
        addr_info_new == curr_addr_info[k] 
        for k, addr_info_new in addr_info_updates.items()
    ])
    doctor_diff = not all([ 
        doctor_info_new == curr_doctor_info[k] 
        for k, doctor_info_new in doctor_info_updates.items()
    ])
    if (not city_diff and 
        not country_diff and 
        not addr_diff and  
        not doctor_diff):
        return {"message": "no updates performed"}

    updates_form = ImmutableMultiDict(list(_updates.items()))
    updates_check = DrRegForm(updates_form)
    if not updates_check.validate():
        m = list(updates_check.errors.items())
        m2 = [{it[0]: it[1][0]} for it in m]
        raise ValueError(m2)
    
    existing_email = db.session.scalar(
        select(Doctor)
        .where(Doctor.email == doctor_info_updates['email'])
        .where(Doctor.user_id != user_id)
    )

    if existing_email:
        return {"error": "Email already exists for another user"}

    new_country_id = 0
    if (country_diff):
        new_country_id = db.session.scalar(
            select(Country.country_id)
            .where(Country.country == _country['country'])
        )
        if not new_country_id:
            new_country = Country(country=_country['country'])
            db.session.add(new_country)
            db.session.flush()
            new_country_id = new_country.country_id
    new_city_id = 0
    if (city_diff):
        new_city_id = db.session.scalar(
            select(City.city_id)
            .where(City.city == _city['city'])
        )
        if not new_city_id:
            new_city = City(
                city=_city['city'],
                country_id=new_country_id or curr_city.country_id
            )
            db.session.add(new_city)
            db.session.flush()
            new_city_id = new_city.city_id
    if (addr_diff):
        new_addr = Address(
            address1=updates.get('address1') or curr_addr_info['address1'], 
            address2=updates.get('address2') or curr_addr_info['address2'],
            city_id=new_city_id or curr_addr_info['city_id'],
            state=updates.get('state') or curr_addr_info['state'],
            zipcode=updates.get('zipcode') or curr_addr_info['zipcode']
        )
        db.session.add(new_addr)
        db.session.flush()
        doctor.address_id = new_addr.address_id
        db.session.flush()
    if (doctor_diff):
        if isinstance(doctor_info_updates.get('accepting_patients'), str):
            if doctor_info_updates['accepting_patients'] in ['false', 'False']:
                doctor_info_updates['accepting_patients'] = False
            elif doctor_info_updates['accepting_patients'] in ['true', 'True']:
                doctor_info_updates['accepting_patients'] = True
            else:
                raise Exception(f"doctor_info_updates['accepting_patients'] is {doctor_info_updates['accepting_patients']}")
        try:
            db.session.execute(
                update(Doctor)
                .where(Doctor.user_id == user_id)
                .values(doctor_info_updates)
            )
        except OperationalError as e:
            raise e

    try:
        db.session.commit()
    except IntegrityError as e:
        raise e
    return {"message": "Doctor updated successfully"}

def assign_survey(doctor_id, patient_id, stars, comment=None, requesting_user: User|None=None):
    if not requesting_user:
        raise NoAuthorizationError('must be authenticated')
    if stars < 1 or stars > 5:
        raise ValueError("Rating must be between 1 and 5")

    dr_pts = Doctor.query.filter_by(user_id=doctor_id).first().patients
    if requesting_user.user_id not in {pt.user_id for pt in dr_pts}:
        raise NoAuthorizationError(f'User with ID: {requesting_user.user_id} is not authorized')

    new_survvey = RatingSurvey(
        doctor_id = doctor_id,
        patient_id = patient_id,
        stars= stars,
        comment=comment
    )

    db.session.add(new_survvey)
    try:
        db.session.commit()
    except Exception as e:
        raise e

    return {
        "message": "Survey Assigned successfully",
        "survey_id": new_survvey.survey_id,
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "stars": stars,
        "comment": comment
    }
