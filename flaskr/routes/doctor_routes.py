from flask import Blueprint, jsonify, request
from flaskr.services import doctor_service, select_doctor

doctor_bp = Blueprint('doctor_bp', __name__, url_prefix='/doctors')

@doctor_bp.route('/', methods=['GET'])
def get_all_doctors():
    doctors = doctor_service.all_doctors()
    return jsonify(doctors), 200

@doctor_bp.route('/<int:doctor_id>', methods=['GET'])
def get_doctor_by_id(doctor_id):
    doctor = doctor_service.doctor_details(doctor_id)
    if doctor:
        return jsonify(doctor), 200
    return jsonify({"error": "Doctor not found"}), 404

@doctor_bp.route('/<int:doctor_id>/request', methods=['POST'])
def request_doctor_by_id(doctor_id):
    # Route to request a doctor as a patient
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    patient_id = data.get('patient_id')
    try:
        select_doctor(doctor_id, patient_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"message": "Doctor requested successfully"}), 200