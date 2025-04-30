from flask import Blueprint, jsonify, request
from flaskr.models import User
from flaskr.services import patient_info, update_patient, token_required, USER_NOT_AUTHORIZED
from flasgger import swag_from

from sqlalchemy.exc import OperationalError, IntegrityError

patient_bp = Blueprint('patient_bp', __name__, url_prefix='/patients')

@patient_bp.route('/info', methods=['GET'])
#@swag_from('../docs/patient_routes/get_patient_info_self_authenticated.yml')
@token_required
def get_patient_info_self_authenticated(user: tuple[int, User]):
    if user[1].account_type.name != 'Patient':
        return jsonify({"message": "user not patient"}), 400
    user_id = user.user_id
    print(f'user_id: {user_id}')
    result = patient_info(user_id)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Patient not found"}), 404

@patient_bp.route('/<int:user_id>/info', methods=['GET'])
#@swag_from('../docs/patient_routes/get_patient_info_other_authenticated.yml')
@token_required
def get_patient_info_other_authenticated2(user: tuple[int, User], user_id):
    # 0) Unpack injected user object (i.e. the user who is making the request)
    _user_id, _user = user
    match _user.account_type.name:
        case 'SuperUser' | 'Patient' if _user_id == user_id:
            pass
        case 'Patient' if _user_id != user_id:
            return USER_NOT_AUTHORIZED(_user_id)
        case 'Doctor' if user_id not in set(
            [p.user_id for p in _user.doctor.patients]):
            return USER_NOT_AUTHORIZED(_user_id)
        case 'Pharmacy' if user_id not in set(
            [p.user_id for p in _user.pharmacy.patients]):
            return USER_NOT_AUTHORIZED(_user_id)
        case _:
            return USER_NOT_AUTHORIZED()
    result = patient_info(user_id)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Patient not found"}), 404

@patient_bp.route('/<int:user_id>', methods=['PUT'])
@swag_from('../docs/patient_routes/update_patient_info.yml')
@token_required
def update_patient_info(user: tuple[int, User], user_id):
    _user_id, _user = user
    match _user.account_type.name:
        case 'SuperUser' | 'Patient' if _user_id == user_id:
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
        return jsonify({"error", error_msg}), 400
    if "error" not in result:
        return jsonify(result), 200
    return jsonify(result), 404