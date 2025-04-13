from werkzeug.datastructures import ImmutableMultiDict      # For type hints
from flask import make_response, jsonify, Response
from flaskr.models import User, Patient, Doctor, Pharmacy, Address, City, Country
from flaskr.extensions import db

from sqlalchemy.exc import IntegrityError                   # For exception handling: Duplicate user creation (unique usernames and emails)
from sqlalchemy import select

from .forms import UserRegistrationForm, PtRegForm, DrRegForm, PharmRegForm

def add_user(user_info: ImmutableMultiDict) -> Response:
    user = UserRegistrationForm(user_info)
    # Validate the form data first
    if not user.validate():
        m = list(user.errors.items())
        m2 = [{it[0]: it[1][0]} for it in m]
        return make_response(jsonify({'error': m2}), 400)
    # Form data for user creation passed; create user object and pass to specific user creation
    country_obj: Country = db.session.scalars(
        select(Country)
        .where(Country.country == user.country.data)
    ).first()
    if not country_obj:
        # New country; create entry
        country_obj = Country(country=user.country.data)
        db.session.add(country_obj)
        db.session.flush()
    country_id = country_obj.country_id
    
    city_obj: City = db.session.scalars(
        select(City)
        .where(City.country_id == country_id)
        .where(City.city == user.city.data)
    ).first()
    if not city_obj:
        # New city; create entry
        city_obj = City(city=user.city.data, country_id=country_id)
        db.session.add(city_obj)
        db.session.flush()
    city_id = city_obj.city_id
    
    address_obj: Address = db.session.scalars(
        select(Address)
        .where(Address.address1 == user.address1.data)
        .where(Address.city_id == city_id)
        .where(Address.state == user.state.data)
        .where(Address.zipcode == user.zipcode.data)
    ).first()
    if not address_obj:
        # New address; create entry
        address_obj = Address(
            address1=user.address1.data,
            address2=user.address2.data if user.address2.data else '',
            city_id=city_id,
            state=user.state.data,
            zipcode=user.zipcode.data
        )
        db.session.add(address_obj)
        db.session.flush()
    address_id = address_obj.address_id
    new_user = User(
        username=user.username.data,
        password=user.password.data,
        account_type=user.account_type.data,
        address_id=address_id
    )
    # Defer the rest of user creation to specific functions per account type
    match user.account_type.data:
        case 'patient':
            return add_patient(user_info, new_user)
        case 'doctor':
            return add_doctor(user_info, new_user)
        case 'pharmacy':
            return add_pharmacy(user_info, new_user)
        case _:
            # This should not be reachable; here for completeness
            return make_response(jsonify({'error':  'unknown server error'}), 500)
    
def add_patient(pt_info: ImmutableMultiDict, user_obj: User) -> Response:
    patient = PtRegForm(pt_info)
    # Validate patient form data first
    if not patient.validate():
        m = list(patient.errors.items())
        return make_response(jsonify({'error': m}), 400)
    # Form validations for patient passed; create object
    new_patient = Patient(
        first_name=patient.first_name.data,
        last_name=patient.last_name.data,
        dob=patient.dob.data,
        email=patient.email.data,
        phone=patient.phone.data,
        user=user_obj
    )
    db.session.add(new_patient)
    try:
        db.session.commit()
    except IntegrityError as e:
        raise e
    except Exception as e:
        m = f'unexpected: {e=}, {type(e)=}'
        return make_response(jsonify({'error': m}), 400)
    else:
        return make_response(jsonify({'user_id': new_patient.user_id}), 201)

def add_doctor(dr_info: ImmutableMultiDict, user_obj: User) -> Response:
    doctor = DrRegForm(dr_info)
    if not doctor.validate():
        m = list(doctor.errors.items())
        return make_response(jsonify({'error': m}), 400)
    new_doctor = Doctor(
        first_name=doctor.first_name.data,
        last_name=doctor.last_name.data,
        dob=doctor.dob.data,
        email=doctor.email.data,
        phone=doctor.phone.data,
        fee=doctor.fee.data,
        license_id=doctor.license_id.data,
        user=user_obj
    )
    db.session.add(new_doctor)
    try:
        db.session.commit()
    except IntegrityError as e:
        raise e
    except Exception as e:
        m = f'unexpected: {e=}, {type(e)=}'
        return make_response(jsonify({'error': m}), 400)
    else:
        return make_response(jsonify({'user_id': new_doctor.user_id}), 201)


def add_pharmacy(pharm_info: ImmutableMultiDict, user_obj: User):
    pharmacy = PharmRegForm(pharm_info)
    if not pharmacy.validate():
        m = list(pharmacy.errors.items())
        return make_response(jsonify({'error': m}), 400)
    new_pharmacy = Pharmacy(
        pharmacy_name=pharmacy.pharmacy_name.data,
        phone=pharmacy.phone.data,
        email=pharmacy.email.data,
        hours=pharmacy.hours.data,
        zipcode=pharmacy.zipcode.data,
        user=user_obj
    )
    db.session.add(new_pharmacy)
    try:
        db.session.commit()
    except IntegrityError as e:
        raise e
    except Exception as e:
        m = f'unexpected: {e=}, {type(e)=}'
        return make_response(jsonify({'error': m}), 400)
    else:
        return make_response(jsonify({'user_id': new_pharmacy.user_id}), 201)