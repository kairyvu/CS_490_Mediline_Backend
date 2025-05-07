from flask_jwt_extended.exceptions import NoAuthorizationError
from flaskr.extensions import db
from flaskr.models.user import Doctor, Patient, Pharmacy, User
from . import patient_info, doctor_details, get_pharmacy_info

def get_user_info_by_id_original(user_id, requesting_user: User|None=None):
    if not requesting_user:
        raise NoAuthorizationError
    is_patient = Patient.query.filter_by(user_id=user_id).first() is not None
    is_doctor = Doctor.query.filter_by(user_id=user_id).first() is not None
    is_pharmacy = Pharmacy.query.filter_by(user_id=user_id).first() is not None

    if not (is_patient or is_doctor or is_pharmacy):
        raise ValueError("User not found as either patient, doctor, or pharmacy")
    if is_patient:
        return patient_info(user_id)
    if is_doctor:
        return doctor_details(user_id)
    if is_pharmacy:
        return get_pharmacy_info(user_id)

def get_user_info_by_id(user_id, requesting_user: User|None=None):
    from flaskr.services import UnauthorizedError
    if not requesting_user:
        raise NoAuthorizationError
    user = User.query.filter_by(user_id=user_id).first()

    acct_type = user.account_type.name
    _acct_type = requesting_user.account_type.name

    match _acct_type:
        case 'SuperUser':
            if acct_type == 'Patient':
                return patient_info(user_id)
            if acct_type == 'Doctor':
                return doctor_details(user_id)
            if acct_type == 'Pharmacy':
                return get_pharmacy_info(user_id)
            if acct_type == 'SuperUser':
                return user.to_dict()
        case 'Patient':
            if ((acct_type == 'Patient') 
                and (user_id == requesting_user.user_id)):
                return patient_info(user_id)
            if acct_type == 'Doctor':
                return doctor_details(user_id)
            if acct_type == 'Pharmacy':
                return get_pharmacy_info(user_id)
            else:
                raise UnauthorizedError
        case 'Doctor':
            _pts = requesting_user.doctor.patients
            if ((acct_type == 'Patient') 
                and (user_id in {p.user_id for p in _pts})):
                # Doctor can only get patient info of patients they take care of
                return patient_info(user_id)
            if acct_type == 'Doctor':
                return doctor_details(user_id)
            if acct_type == 'Pharmacy':
                return get_pharmacy_info(user_id)
            else:
                raise UnauthorizedError
        case 'Pharmacy':
            _pts = requesting_user.pharmacy.patients
            if ((acct_type == 'Patient') 
                and (user_id in {p.user_id for p in _pts})):
                # Pharmacy can only get patient info of patients they take care of
                return patient_info(user_id)
            if acct_type == 'Doctor':
                return doctor_details(user_id)
            if acct_type == 'Pharmacy':
                return get_pharmacy_info(user_id)
            else:
                raise UnauthorizedError
        case _:
            raise Exception('Unknown server error')
        