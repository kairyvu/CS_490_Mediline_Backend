from flask import Blueprint, jsonify, request
from flasgger import swag_from
from flaskr.services import doctor_service, select_doctor
from sqlalchemy.exc import OperationalError, IntegrityError

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
    return jsonify({"total_patients": doctor_service.total_patients(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/upcoming-appointments/count', methods=['GET'])
@swag_from('../docs/doctor_routes/count_upcoming_appointments.yml')
def count_upcoming_appointments(doctor_id):
    return jsonify({"upcoming_appointments_count": doctor_service.upcoming_appointments_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/pending-appointments/count', methods=['GET'])
@swag_from('../docs/doctor_routes/count_pending_appointments.yml')
def count_pending_appointments(doctor_id):
    return jsonify({"pending_appointments_count": doctor_service.pending_appointments_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/doctor-patients/count', methods=['GET'])
@swag_from('../docs/doctor_routes/count_doctor_patients.yml')
def count_doctor_patients(doctor_id):
    return jsonify({"doctor_patients_count": doctor_service.doctor_patients_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/patients-today', methods=['GET'])
@swag_from('../docs/doctor_routes/patients_today.yml')
def patients_today(doctor_id):
    date = request.args.get('date')
    return jsonify(doctor_service.todays_patient(doctor_id, date)), 200

@doctor_bp.route('/<int:doctor_id>/ratings', methods=['GET'])
@swag_from('../docs/doctor_routes/doctor_ratings.yml')
def doctor_ratings(doctor_id):
    sort_by = request.args.get('sort_by', 'stars')
    order = request.args.get('order', 'desc')
    try:
        return jsonify(doctor_service.doctor_rating_detail(doctor_id, sort_by, order)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@doctor_bp.route('/<int:doctor_id>/patient/<int:patient_id>/last-completed', methods=['GET'])
@swag_from('../docs/doctor_routes/last_completed_appointment.yml')
def last_completed_appointment(patient_id, doctor_id):
    return jsonify(doctor_service.last_completed_appointment(patient_id, doctor_id)), 200

@doctor_bp.route('/<int:doctor_id>/discussions', methods=['GET'])
@swag_from('../docs/doctor_routes/doctor_general_discussions.yml')
def doctor_general_discussions(doctor_id):
    return jsonify(doctor_service.doctor_general_discussion(doctor_id)), 200

@doctor_bp.route('/<int:doctor_id>/appointment_requests', methods=['GET'])
@swag_from('../docs/doctor_routes/new_appointment_requests.yml')
def new_appointment_requests(doctor_id):
    appointments = doctor_service.new_appointments_request(doctor_id)
    return jsonify(appointments), 200


@doctor_bp.route('/<int:user_id>', methods=['PUT'])
def update_doctor_info(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "no input data provided"}), 400
    try:
        result = doctor_service.update_doctor(user_id, data)
    except ValueError as e:
        return jsonify({
            "error": "invalid fields",
            "fields": e.args[0]}), 400
    except OperationalError as e:
        error_msg = (str(e).split(' ', 1)[1]).partition('\n')[0].split(' ', 1)[1]
        return jsonify({"error": error_msg}), 504
    except IntegrityError as e:
        error_msg = str((str(e.args[0]).split(maxsplit=1))[1]).split(',')[1].strip().strip(')"\\')
        return jsonify({"error", error_msg}), 400
    if "error" not in result:
        return jsonify(result), 200
    return jsonify(result), 404
