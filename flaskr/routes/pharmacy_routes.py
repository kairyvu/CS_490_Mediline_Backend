
from kombu.exceptions import OperationalError as MQOpErr
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flaskr.models import User
from flaskr.services import get_all_pharmacy_patients, add_pt_rx, USER_NOT_AUTHORIZED
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
        case 'SuperUser' | 'Pharmacy' if _user_id == pharmacy_id:
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
@swag_from('../docs/pharmacy_routes/post_patient_prescription.yml')
def post_patient_prescription(pharmacy_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    med_schema = {'dosage', 'instructions', 'medication_id'}
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    medications = data.get('medications')

    # perform validation
    if not all([patient_id, doctor_id, medications]):
        return jsonify(error='missing required fields'), 400
    if len(medications) == 0:
        return jsonify(error='no medications in prescription'), 400
    if not all([isinstance(med, dict) for med in medications]):
        return jsonify(error='medications must be json objects'), 400
    for med in medications:
        schema_diff = set(med) - med_schema
        if schema_diff:
            return jsonify({
                'error': "schema doesn't conform",
                'invalid': list(schema_diff)
            }), 400
        if not all([attr in med_schema for attr in med]):
            return jsonify({
                'error': f'medication {med} has missing attributes'
            }), 400
    try:
        res = add_pt_rx(pharmacy_id, patient_id, doctor_id, medications)
    except MQOpErr as e:
        return jsonify({'error': 'failed to send prescription'}), 500
    except Exception as e:
        print(type(e))
        return jsonify({'error': f'{str(e)}'}), 500
    if res == 'PENDING':
        return jsonify({
            'message': 'prescription submitted successfully'
        }), 202         # 202 to indicate async operation
    return jsonify({'error': 'failed to send prescription'}), 500