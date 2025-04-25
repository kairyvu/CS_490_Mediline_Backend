from werkzeug.datastructures import ImmutableMultiDict
from sqlalchemy import select, update
from flaskr.models import Patient, Doctor, Pharmacy, User, Address, City, Country
from flaskr.models import MedicalRecord
from flaskr.extensions import db
from .forms import UserRegistrationForm
from datetime import datetime

from sqlalchemy.exc import OperationalError, IntegrityError

def get_patient_info(user_id):
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return None

    doctor: Doctor = Doctor.query.filter_by(user_id=patient.doctor_id).first()
    pharmacy: Pharmacy = Pharmacy.query.filter_by(user_id=patient.pharmacy_id).first()

    return {
        "user_id": patient.user_id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "email": patient.email,
        "phone": patient.phone,
        "dob": str(patient.dob),
        "doctor": {
            "first_name": doctor.first_name,
            "last_name": doctor.last_name,
            "specialization": doctor.specialization,
            "fee" : doctor.fee,
            "phone": doctor.phone,
            "email": doctor.email
        } if doctor else None,
        "pharmacy": {
            "pharmacy_name": pharmacy.pharmacy_name,
            "phone": pharmacy.phone,
            "email": pharmacy.email,
            "hours": pharmacy.hours,
            "zipcode": pharmacy.user.address.zipcode,
            "address1": pharmacy.user.address.address1,
            "address2": pharmacy.user.address.address2,
            "city": pharmacy.user.address.city.city,
            "state": pharmacy.user.address.state,
            "country": pharmacy.user.address.city.country.country,
        } if pharmacy else None,
        "address1": patient.user.address.address1,
        "address2": patient.user.address.address2,
        "city": patient.user.address.city.city,
        "state": patient.user.address.state,
        "zipcode": patient.user.address.zipcode,
        "country": patient.user.address.city.country.country
    }

def update_patient(user_id, updates: dict) -> dict:
    #patient: Patient = Patient.query.filter_by(user_id=user_id).first()
    patient: User = db.session.scalar(
        select(User)
        .where(User.user_id == user_id)
    )
    if not patient:
        return {"error": "Patient not found"}

    # Attributes that can be edited through this route
    address_attr = {'address1', 'address2', 'state', 'zipcode'}
    patient_attr = {'first_name', 'last_name', 'email', 'phone', 'dob'}

    # Check provided updates payload if it's a subset of the allowed attributes
    invalid_attrs = set(updates) - (patient_attr 
                                    | address_attr 
                                    | {'city', 'country'})
    if len(invalid_attrs) != 0: 
        return {
            "message": "no updates performed",
            "invalid_attributes": list(invalid_attrs)
        }

    ### Do validation on updates by passing it to reg form
    ## Check all provided attributes, fill missing with known attr
    # Fetch city and country
    curr_pt_info = patient.patient.to_dict()
    curr_addr_info = patient.address.to_dict()
    curr_city = db.session.scalar( 
        select(City)
        .where(City.city_id == patient.address.city.city_id)
    )
    curr_country = db.session.scalar(
        select(Country)
        .where(Country.country_id == curr_city.country_id)
    )
    _city = {'city': updates.get('city') or curr_city.city}
    _country = {'country': updates.get('country') or curr_country.country}
    # For each attribute in allowed attributes, note the changed value
    # as given from `updates`; else, set the value as the already set value
    pt_info_updates = {
        attr: 
            updates.get(attr) 
            or curr_pt_info[attr] 
            for attr in patient_attr
    }
    addr_info_updates = {
        attr: 
            updates.get(attr) 
            or curr_addr_info[attr] 
            for attr in address_attr
    }
    _updates = pt_info_updates | addr_info_updates | _city | _country
    _updates.update({
        'username': patient.username,
        'password': patient.password,
        'account_type': 'patient'
    })

    # Check all provided data if its different
    # True if difference
    city_diff = curr_city.city != _city['city']
    country_diff = curr_country.country != _country['country']
    addr_diff = not all([ 
        addr_info_new == curr_addr_info[k] 
        for k, addr_info_new in addr_info_updates.items()
    ])
    pt_diff = not all([ 
        pt_info_new == curr_pt_info[k] 
        for k, pt_info_new in pt_info_updates.items()
    ])
    if (not city_diff and 
        not country_diff and 
        not addr_diff and  
        not pt_diff):
        return {"message": "no updates performed"}

    # Pass to registration form
    updates_form = ImmutableMultiDict(list(_updates.items()))
    updates_check = UserRegistrationForm(updates_form)
    if not updates_check.validate():
        m = list(updates_check.errors.items())
        m2 = [{it[0]: it[1][0]} for it in m]
        raise ValueError(m2)

    # Perform updates
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
        # Insert on address difference because other patients 
        # may have same address
        new_addr = Address(
            address1=updates.get('address1') or curr_addr_info['address1'], 
            address2=updates.get('address2') or curr_addr_info['address2'],
            city_id=new_city_id or curr_addr_info['city_id'],
            state=updates.get('state') or curr_addr_info['state'],
            zipcode=updates.get('zipcode') or curr_addr_info['zipcode']
        )
        db.session.add(new_addr)
        db.session.flush()
        patient.address_id = new_addr.address_id
        db.session.flush()
    if (pt_diff):
        try:
            db.session.execute(
                update(Patient)
                .where(Patient.user_id == user_id)
                .values(pt_info_updates)
            )
        except OperationalError as e:
            raise e

    try:
        db.session.commit()
    except IntegrityError as e:
        raise e
    return {"message": "Patient updated successfully"}

def patient_medical_history(patient_id):
    patient = Patient.query.filter_by(user_id = patient_id).first()
    if not patient:
        return None
    
    records = MedicalRecord.query.filter_by(patient_id = patient_id).order_by(MedicalRecord.created_at.desc()).all()

    return{
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "medical_record":[
            {
                "record_id": r.medical_record_id,
                "description": r.description,
                "creadted_at": r.created_at.strftime("%Y-%m-%d %I:%M %p")
            }
            for r in records
        ]
    }

def create_medical_record(patient_id, description):
    patient =Patient.query.filter_by(user_id = patient_id).first()
    if not patient:
        return None
    
    record = MedicalRecord(
        patient_id = patient_id,
        description = description,
        created_at = datetime.now()
    )

    db.session.add(record)
    db.session.commit()
    return{
        "record_id": record.medical_record_id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "description": record.description,
        "created_at": record.created_at.strftime("%Y-%m-%d %I:%M %p")
    }