
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flaskr.models import User
from flaskr.services import get_all_pharmacy_patients, add_pt_rx, USER_NOT_AUTHORIZED, validate_rx
from flasgger import swag_from

pharmacy_bp = Blueprint('pharmacy', __name__)
@pharmacy_bp.route('/<int:pharmacy_id>/patients', methods=['GET'])
@jwt_required()
@swag_from('../docs/pharmacy_routes/get_pharmacy_patients.yml')
def get_pharmacy_patients(pharmacy_id):
    _user: User = current_user
    _user_id = _user.user_id
    _acct_type = _user.account_type.name
    match _acct_type:
        case 'SuperUser':
            pass
        case 'Pharmacy' if _user_id == pharmacy_id:
            pass
        case _:
            return USER_NOT_AUTHORIZED(_user_id)
    try:
        history = get_all_pharmacy_patients(pharmacy_id=pharmacy_id)
        return jsonify(history), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medications history'}), 500

# This route is only returning {'message': 'ok', 'status': 202} for now and not working as intended
@pharmacy_bp.route('/<int:pharmacy_id>', methods=['POST'])
@swag_from('../docs/pharmacy_routes/post_patient_prescription.yml')
def post_patient_prescription(pharmacy_id):
    if not (result := validate_rx(request.get_json())):
        return result
    patient_id, doctor_id, medications = result
    try:
        res = add_pt_rx(pharmacy_id, patient_id, doctor_id, medications)
    except Exception as e:
        print(type(e))
        return jsonify({'error': f'{str(e)}'}), 500
    if res:
        return jsonify({
            'message': 'prescription submitted successfully'
        }), 202         # 202 to indicate async operation
    return jsonify({'error': 'failed to send prescription'}), 500