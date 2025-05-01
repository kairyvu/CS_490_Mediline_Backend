from flask import Blueprint, jsonify, request
from flaskr.services import all_doctors, doctor_details, total_patients, upcoming_appointments_count, pending_appointments_count, doctor_patients_count, todays_patient, doctor_rating_detail, last_completed_appointment, doctor_general_discussion, select_doctor 
from flasgger import swag_from

doctor_bp = Blueprint('doctor_bp', __name__)

@doctor_bp.route('/', methods=['GET'])
@swag_from('../docs/doctor_routes/get_all_doctors.yml')
def get_all_doctors():
    doctors = all_doctors()
    return jsonify(doctors), 200

@doctor_bp.route('/<int:doctor_id>/request', methods=['POST'])
@swag_from('../docs/doctor_routes/request_doctor_by_id.yml')
def request_doctor_by_id(doctor_id):
    # Route to request a doctor as a patient
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    patient_id = data.get('patient_id')
    if not patient_id:
        return jsonify({"error": "patient id is required"}), 400
    try:
        select_doctor(doctor_id, patient_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Doctor requested successfully"}), 200

@doctor_bp.route('/<int:doctor_id>/total-patients', methods=['GET'])
def total(doctor_id):
    return jsonify({"total_patients": total_patients(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/upcoming-appointments/count', methods=['GET'])
@swag_from('../docs/doctor_routes/count_upcoming_appointments.yml')
def count_upcoming_appointments(doctor_id):
    return jsonify({"upcoming_appointments_count": upcoming_appointments_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/pending-appointments/count', methods=['GET'])
@swag_from('../docs/doctor_routes/count_pending_appointments.yml')
def count_pending_appointments(doctor_id):
    return jsonify({"pending_appointments_count": pending_appointments_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/doctor-patients/count', methods=['GET'])
@swag_from('../docs/doctor_routes/count_doctor_patients.yml')
def count_doctor_patients(doctor_id):
    return jsonify({"doctor_patients_count": doctor_patients_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/patients-today', methods=['GET'])
@swag_from('../docs/doctor_routes/patients_today.yml')
def patients_today(doctor_id):
    date = request.args.get('date')
    return jsonify(todays_patient(doctor_id, date)), 200

@doctor_bp.route('/<int:doctor_id>/ratings', methods=['GET'])
@swag_from('../docs/doctor_routes/doctor_ratings.yml')
def doctor_ratings(doctor_id):
    sort_by = request.args.get('sort_by', 'stars')
    order = request.args.get('order', 'desc')
    try:
        return jsonify(doctor_rating_detail(doctor_id, sort_by, order)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@doctor_bp.route('/<int:doctor_id>/patient/<int:patient_id>/last-completed', methods=['GET'])
@swag_from('../docs/doctor_routes/last_completed_appointment.yml')
def last_completed_appointment(patient_id, doctor_id):
    return jsonify(last_completed_appointment(patient_id, doctor_id)), 200

@doctor_bp.route('/<int:doctor_id>/discussions', methods=['GET'])
@swag_from('../docs/doctor_routes/doctor_general_discussions.yml')
def doctor_general_discussions(doctor_id):
    return jsonify(doctor_general_discussion(doctor_id)), 200
