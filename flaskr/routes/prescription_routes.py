from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flaskr.models import User
from flaskr.services import get_medications_by_prescription, get_prescriptions, \
    get_prescription_count_by_pharmacy, get_pharmacy_medications_inventory, \
    get_medications_history_by_patient, USER_NOT_AUTHORIZED, UnauthorizedError
from flasgger import swag_from

prescription_bp = Blueprint("prescription", __name__)

@prescription_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/prescription_routes/get_prescription_by_user.yml')
def get_prescription_by_user(user_id):
    _user_id = current_user.user_id
    _acct_type = current_user.account_type.name
    if (_user_id != user_id) and (_acct_type != 'SuperUser'):
        return USER_NOT_AUTHORIZED(_user_id)
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'asc')

    try:
        prescriptions = get_prescriptions(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(prescriptions), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@prescription_bp.route('/<int:prescription_id>/medications', methods=['GET'])
@jwt_required()
@swag_from('../docs/prescription_routes/get_medication_list.yml')
def get_medication_list(prescription_id):
    try:
        medications = get_medications_by_prescription(prescription_id, 
                                                      requesting_user=current_user)
        return jsonify(medications), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except UnauthorizedError as e:
        return USER_NOT_AUTHORIZED(current_user.user_id)
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medications'}), 500

## TODO: Documentation
@prescription_bp.route('/pharmacy/<int:pharmacy_id>/count', methods=['GET'])
@jwt_required()
def get_prescription_count(pharmacy_id):
    _user_id = current_user.user_id
    _acct_type = current_user.account_type.name
    if (_user_id != pharmacy_id) and (_acct_type != 'SuperUser'):
        return USER_NOT_AUTHORIZED(_user_id)
    try:
        count = get_prescription_count_by_pharmacy(pharmacy_id)
        return jsonify(count), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the prescription count'}), 500

## TODO: Documentation
@prescription_bp.route('/pharmacy/<int:pharmacy_id>/inventory', methods=['GET'])
@jwt_required()
def get_pharmacy_inventory(pharmacy_id):
    _user_id = current_user.user_id
    _acct_type = current_user.account_type.name
    if (_user_id != pharmacy_id) and (_acct_type != 'SuperUser'):
        return USER_NOT_AUTHORIZED(_user_id)
    try:
        inventory = get_pharmacy_medications_inventory(pharmacy_id)
        return jsonify(inventory), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the pharmacy inventory'}), 500
    
## TODO: Documentation
@prescription_bp.route('/patient/<int:patient_id>/history', methods=['GET'])
@jwt_required()
def get_medications_history(patient_id):
    _user: User = current_user
    _user_id = _user.user_id
    _acct_type = _user.account_type.name
    match _acct_type:
        case 'SuperUser' | 'Patient' if _user_id == patient_id:
            pass
        case 'Doctor' if patient_id in set([
            p.user_id for p in _user.doctor.patients]):
            pass
        case 'Pharmacy' if patient_id in set([
            p.user_id for p in _user.pharmacy.patients]):
            pass
        case _:
            return USER_NOT_AUTHORIZED(_user_id)
    try:
        history = get_medications_history_by_patient(patient_id)
        return jsonify(history), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medications history'}), 500