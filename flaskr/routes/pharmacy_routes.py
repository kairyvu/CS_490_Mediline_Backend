
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, current_user
from flaskr.models import User
from flaskr.services import get_all_pharmacy_patients, add_pt_rx, \
    USER_NOT_AUTHORIZED, validate_rx, check_rx_auth, fetch_rx_requests, handle_rx_request, validate_body
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

@pharmacy_bp.route('/<int:pharmacy_id>', methods=['POST'])
@jwt_required()
@swag_from('../docs/pharmacy_routes/post_patient_prescription.yml')
def post_patient_prescription(pharmacy_id):
    # Checking ok payload
    if not (result := validate_rx(request.get_json())):
        return result
    patient_id, doctor_id, medications = result
    is_authorized = check_rx_auth(patient_id, doctor_id, pharmacy_id, current_user)
    if not is_authorized:
        return USER_NOT_AUTHORIZED(current_user.user_id)
    try:
        res = add_pt_rx(pharmacy_id, patient_id, doctor_id, medications)
    except Exception as e:
        print(type(e))
        print(str(e))
        return jsonify({'error': f'{str(e)}'}), 500
    if res:
        return jsonify({
            'message': 'prescription submitted successfully'
        }), 202         # 202 to indicate async operation
    return jsonify({'error': 'failed to send prescription'}), 500

@pharmacy_bp.route('/<int:pharmacy_id>/requests', methods=['GET', 'DELETE'])
def get_new_prescriptions(pharmacy_id):
    if request.method == 'GET':
        try:
            res = fetch_rx_requests(pharmacy_id)
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500
        return jsonify({'msg': 'ok'})
    elif request.method == 'DELETE':
        if isinstance((res := validate_body(request.get_json())), Response):
            return res, 400
        rx_id, status = res
        try:
            res2 = handle_rx_request(pharmacy_id, rx_id, status)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500
        return jsonify({'msg': 'deleted'}), 204
