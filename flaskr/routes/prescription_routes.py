from flask import Blueprint, jsonify, request
from flaskr.services import get_medications_by_prescription, get_prescriptions
from flasgger import swag_from

prescription_bp = Blueprint("prescription", __name__)
@prescription_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from('../docs/prescription_routes/get_prescription_by_user.yml')
def get_prescription_by_user(user_id):
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'asc')

    try:
        prescriptions = get_prescriptions(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(prescriptions), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@prescription_bp.route('/<int:prescription_id>/medications', methods=['GET'])
@swag_from('../docs/prescription_routes/get_medication_list.yml')
def get_medication_list(prescription_id):
    try:
        medications = get_medications_by_prescription(prescription_id)
        return jsonify(medications), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medications'}), 500