from flask import Blueprint, jsonify, request
from flaskr.services import patient_service

patient_bp = Blueprint('patient_bp', __name__, url_prefix='/patients')

@patient_bp.route('/<int:user_id>/info', methods=['GET'])
def get_patient_info(user_id):
    result = patient_service.get_patient_info(user_id)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Patient not found"}), 404

@patient_bp.route('/<int:user_id>', methods=['PUT'])
def update_patient_info(user_id):
    data = request.get_json()
    result = patient_service.update_patient(user_id, data)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Patient not found"}), 404