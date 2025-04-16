from flask import Blueprint, jsonify, request
from flaskr.services import doctor_service
from flasgger import swag_from

doctor_bp = Blueprint('doctor_bp', __name__, url_prefix='/doctors')

@doctor_bp.route('/', methods=['GET'])
@swag_from('../docs/doctor_routes/get_all_doctors.yml')
def get_all_doctors():
    doctors = doctor_service.all_doctors()
    return jsonify(doctors), 200

@doctor_bp.route('/<int:doctor_id>', methods=['GET'])
@swag_from('../docs/doctor_routes/get_doctor_by_id.yml')
def get_doctor_by_id(doctor_id):
    doctor = doctor_service.doctor_details(doctor_id)
    if doctor:
        return jsonify(doctor), 200
    return jsonify({"error": "Doctor not found"}), 404


