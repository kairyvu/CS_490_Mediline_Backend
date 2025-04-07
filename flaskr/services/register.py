from werkzeug.datastructures import ImmutableMultiDict
from flask import make_response, jsonify
from flaskr.models import User, Patient, Doctor, Pharmacy
from flaskr.extensions import db

from .forms import UserRegistrationForm, PtRegForm, DrRegForm, PharmRegForm

def add_user(user_info: ImmutableMultiDict):
    user = UserRegistrationForm(user_info)
    # Validate the form data first
    if not user.validate():
        m = list(user.errors.items())
        return make_response(jsonify(message=m), 400)
    match user.account_type.data:
        case 'patient':
            return add_patient(user_info)
        case 'doctor':
            return add_doctor(user_info)
        case 'pharmacy':
            return add_pharmacy(user_info)
        case _:
            return make_response(jsonify(message='unknown account type'), 400)
    #return make_response(jsonify(message='good'), 200)
    
def add_patient(pt_info):
    patient = PtRegForm(pt_info)
    # Validate the form data first
    if not patient.validate():
        m = list(patient.errors.items())
        return make_response(jsonify(message=m), 400)
    return make_response(jsonify(message='good'), 201)

def add_doctor(dr_info):
    pass

def add_pharmacy(pharm_info):
    pass


    """
    ## Check needed form data present from args
    valid = validate_form_data(needed_keys, user_info)
    if not valid[0]: 
        return make_response(jsonify(message=valid[1]), 400)
    else:
        match user_info['account_type']:
            case 'patient':
                return add_patient(user_info)
            case 'doctor':
                return add_doctor(user_info)
            case 'pharmacy':
                return add_pharmacy(user_info)
            case _:
                return make_response(jsonify(message='unknown account type'), 400)
    """

"""
def add_patient(pt_info):
    valid = validate_form_data(needed_keys_pt, pt_info)
    if not valid[0]:
        return make_response(jsonify(message=valid[1]), 400)
    return make_response(jsonify(message='patient added'), 201)

def add_doctor(dr_info):
    valid = validate_form_data(needed_keys_dr, dr_info)
    if not valid[0]:
        return make_response(jsonify(message=valid[1]), 400)
    return make_response(jsonify(message='doctor added'), 201)

def add_pharmacy(pharm_info):
    valid = validate_form_data(needed_keys_pharm, pharm_info)
    if not valid[0]:
        return make_response(jsonify(message=valid[1]), 400)
    return make_response(jsonify(message='pharmacy added'), 201)
"""



## OLD
''' how to select all users from users
from sqlalchemy import select
users = db.session.execute(select(User)).scalars().all()
users_list: list[dict] = []
for user in users:
    u_dict = user.__dict__
    u_dict.pop('_sa_instance_state')
    u_dict['account_type'] = u_dict['account_type'].value
    users_list.append(u_dict)
return jsonify(users_list)

### OLD ###
needed_keys: list[str] = [
    'username',
    'password', 
    'account_type',
    'email',
    'phone'
]


needed_keys_pt: list[str] = [
    'first_name',
    'last_name',
    'dob',
]

needed_keys_dr: list[str] = needed_keys_pt + [
    'specialization',
    'fee',
    'license_id'
]

needed_keys_pharm: list[str] = [
    'pharmacy_name',
    'hours',
    'zipcode'
]

def validate_form_data(needed: list[str], json_data: dict[str, str]) -> tuple[bool, str]:
    key_mask = list(key in json_data for key in needed)
    if not all(key_mask):
        missing = [y for x, y in zip(key_mask, needed) if not x]
        return (False, f'malformed form data: missing field(s): {missing}')
    return (True, '')

'''