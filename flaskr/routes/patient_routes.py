from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flaskr.models import User
from flaskr.services import patient_info, update_patient, update_primary_pharmacy, USER_NOT_AUTHORIZED
from flasgger import swag_from

from sqlalchemy.exc import OperationalError, IntegrityError

patient_bp = Blueprint('patient_bp', __name__)

@patient_bp.route('/info', methods=['GET'])
@jwt_required()
@swag_from('../docs/patient_routes/get_patient_info_self_authenticated.yml')
def get_patient_info_self_authenticated():
    user_id = current_user.user_id
    result = patient_info(user_id)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Patient not found"}), 404

@patient_bp.route('/<int:user_id>/info', methods=['GET'])
@jwt_required()
@swag_from('../docs/patient_routes/get_patient_info_other_authenticated.yml')
def get_patient_info_other_authenticated(user_id):
    _user: User = current_user
    _user_id = _user.user_id
    assert isinstance(_user, User)
    print(_user.account_type.name)
    print(set(p.user_id for p in _user.doctor.patients))
    match _user.account_type.name:
        case 'SuperUser': 
            pass
        case 'Patient' if _user_id == user_id:
            pass
        case 'Patient' if _user_id != user_id:
            return USER_NOT_AUTHORIZED(_user_id)
        case 'Doctor':
            if user_id not in set(
                [p.user_id for p in _user.doctor.patients]):
                return USER_NOT_AUTHORIZED(_user_id)
            else:
                pass
        case 'Pharmacy':
            if user_id not in set(
                [p.user_id for p in _user.pharmacy.patients]):
                return USER_NOT_AUTHORIZED(_user_id)
            else:
                pass
        case _:
            return USER_NOT_AUTHORIZED()
    result = patient_info(user_id)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Patient not found"}), 404

@patient_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@swag_from('../docs/patient_routes/update_patient_info.yml')
def update_patient_info(user_id):
    _user: User = current_user
    _user_id = _user.user_id
    match _user.account_type.name:
        case 'SuperUser':
            pass
        case 'Patient' if _user_id == user_id:
            pass
        case 'Patient' if _user_id != user_id:
            print('here')
            return USER_NOT_AUTHORIZED(_user_id)
        case _:
            print('here..?')
            return USER_NOT_AUTHORIZED(_user_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "no input data provided"}), 400
    try:
        result = update_patient(user_id, data)
    except ValueError as e:
        return jsonify({
            "error": "invalid fields",
            "fields": e.args[0]}), 400
    except OperationalError as e:
        error_msg = (str(e).split(' ', 1)[1]).partition('\n')[0].split(' ', 1)[1]
        return jsonify({"error": error_msg}), 504
    except IntegrityError as e:
        error_msg = str((str(e.args[0]).split(maxsplit=1))[1]).split(',')[1].strip().strip(')"\\')
        return jsonify({"error": error_msg}), 400
    if "error" not in result:
        return jsonify(result), 200
    return jsonify(result), 404

@patient_bp.route('/<int:patient_id>/pharmacy', methods=['PUT'])
@jwt_required()
@swag_from('../docs/patient_routes/update_primary_pharmacy.yml')
def primary_pharmacy(patient_id):
    if ((current_user.account_type.name != 'SuperUser') 
        and (current_user.user_id != patient_id)):
        return USER_NOT_AUTHORIZED(current_user.user_id)
    data = request.get_json()
    pharmacy_id = data.get("pharmacy_id")
    if not pharmacy_id:
        return jsonify({"error": "Pharmacy ID is required"}), 400

    result = update_primary_pharmacy(patient_id, pharmacy_id)
    if result == "Patient not found":
        return jsonify({"error": "Patient not found"}), 404
    elif result == "Pharmacy not found":
        return jsonify({"error": "Pharmacy not found"}), 404
    else:
        return jsonify(result), 200
    

    
