from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flaskr.services import doctor_service, select_doctor

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

@doctor_bp.route('/<int:doctor_id>/total-patients', methods=['GET'])
def total(doctor_id):
    return jsonify({"total_patients": doctor_service.total_patients(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/upcoming-appointments/count', methods=['GET'])
def count_upcoming_appointments(doctor_id):
    return jsonify({"upcoming_appointments_count": doctor_service.upcoming_appointments_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/pending-appointments/count', methods=['GET'])
def count_pending_appointments(doctor_id):
    return jsonify({"pending_appointments_count": doctor_service.pending_appointments_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/doctor-patients/count', methods=['GET'])
def count_doctor_patients(doctor_id):
    return jsonify({"doctor_patients_count": doctor_service.doctor_patients_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/patients-today', methods=['GET'])
def patients_today(doctor_id):
    date = request.args.get('date')
    return jsonify(doctor_service.todays_patient(doctor_id, date)), 200

@doctor_bp.route('/<int:doctor_id>/ratings', methods=['GET'])
def doctor_ratings(doctor_id):
    sort_by = request.args.get('sort_by', 'stars')
    order = request.args.get('order', 'desc')
    try:
        return jsonify(doctor_service.doctor_rating_detail(doctor_id, sort_by, order)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@doctor_bp.route('/<int:doctor_id>/patient/<int:patient_id>/last-completed', methods=['GET'])
def last_completed_appointment(patient_id, doctor_id):
    return jsonify(doctor_service.last_completed_appointment(patient_id, doctor_id)), 200

@doctor_bp.route('/<int:doctor_id>/discussions', methods=['GET'])
def doctor_general_discussions(doctor_id):
    return jsonify(doctor_service.doctor_general_discussion(doctor_id)), 200
