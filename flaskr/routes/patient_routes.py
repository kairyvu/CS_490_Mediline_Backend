from flask import Blueprint, jsonify, request
from flaskr.services import patient_service
from flasgger import swag_from

patient_bp = Blueprint('patient_bp', __name__, url_prefix='/patients')

@patient_bp.route('/<int:user_id>/info', methods=['GET'])
@swag_from('../docs/patient_routes/get_patient_info.yml')
def get_patient_info(user_id):
    result = patient_service.get_patient_info(user_id)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Patient not found"}), 404

@patient_bp.route('/<int:user_id>', methods=['PUT'])
@swag_from('../docs/patient_routes/update_patient_info.yml')
def update_patient_info(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "no input data provided"}), 400
    result = patient_service.update_patient(user_id, data)
    if "error" not in result:
        return jsonify(result), 200
    return jsonify(result), 404