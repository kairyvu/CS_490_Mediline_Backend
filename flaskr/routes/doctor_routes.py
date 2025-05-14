from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flask_jwt_extended.exceptions import NoAuthorizationError
from flaskr.services import all_doctors, doctor_details, \
    upcoming_appointments_count, pending_appointments_count, \
    doctor_patients_count_and_list, todays_patient, doctor_rating_detail, new_appointments_request, update_doctor,\
    last_completed_appointment, doctor_general_discussion, assign_survey,\
    USER_NOT_AUTHORIZED, all_specialties
from flasgger import swag_from
from sqlalchemy.exc import OperationalError, IntegrityError


doctor_bp = Blueprint('doctor_bp', __name__)

### ---PUBLIC ROUTES---
@doctor_bp.route('/', methods=['GET'], strict_slashes=False)
@swag_from('../docs/doctor_routes/get_all_doctors.yml')
def get_all_doctors():
    sort_by = request.args.get('sort_by', 'user_id')
    order = request.args.get('order', 'asc')

    try:
        doctors = all_doctors(sort_by=sort_by, order=order)
        return jsonify(doctors), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@doctor_bp.route('/<int:doctor_id>/ratings', methods=['GET'])
@swag_from('../docs/doctor_routes/doctor_ratings.yml')
def doctor_ratings(doctor_id):
    sort_by = request.args.get('sort_by', 'stars')
    order = request.args.get('order', 'desc')
    try:
        return jsonify(doctor_rating_detail(doctor_id, sort_by, order)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@doctor_bp.route('/specialties', methods=['GET'])
@swag_from('../docs/doctor_routes/specialties.yml')
def doctor_specialties():
    order = request.args.get('order', 'asc')

    try:
        s_ls = all_specialties(order=order)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(s_ls), 200
### ---END PUBLIC ROUTES---

### ---PROTECTED ROUTES---
@doctor_bp.route('/<int:doctor_id>/doctor-patients', methods=['GET'])
@jwt_required()
@swag_from('../docs/doctor_routes/doctor_patients_count_details.yml')
def doctor_patients_count_details(doctor_id):
    if (current_user.user_id != doctor_id 
        and current_user.account_type.name != 'SuperUser'):
        return USER_NOT_AUTHORIZED(current_user.user_id)
    return jsonify(doctor_patients_count_and_list(doctor_id)), 200

@doctor_bp.route('/<int:doctor_id>/upcoming-appointments/count', methods=['GET'])
@jwt_required()
@swag_from('../docs/doctor_routes/count_upcoming_appointments.yml')
def count_upcoming_appointments(doctor_id):
    if (current_user.user_id != doctor_id 
        and current_user.account_type.name != 'SuperUser'):
        return USER_NOT_AUTHORIZED(current_user.user_id) 
    return jsonify({"upcoming_appointments_count": upcoming_appointments_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/pending-appointments/count', methods=['GET'])
@jwt_required()
@swag_from('../docs/doctor_routes/count_pending_appointments.yml')
def count_pending_appointments(doctor_id):
    if (current_user.user_id != doctor_id 
        and current_user.account_type.name != 'SuperUser'):
        return USER_NOT_AUTHORIZED(current_user.user_id) 
    return jsonify({"pending_appointments_count": pending_appointments_count(doctor_id)}), 200

@doctor_bp.route('/<int:doctor_id>/patients-today', methods=['GET'])
@jwt_required()
@swag_from('../docs/doctor_routes/patients_today.yml')
def patients_today(doctor_id):
    if (current_user.user_id != doctor_id 
        and current_user.account_type.name != 'SuperUser'):
        return USER_NOT_AUTHORIZED(current_user.user_id) 
    date = request.args.get('date')
    return jsonify(todays_patient(doctor_id, date)), 200
    
@doctor_bp.route('/<int:doctor_id>/patient/<int:patient_id>/last-completed', methods=['GET'])
@jwt_required()
@swag_from('../docs/doctor_routes/last_completed_appointment.yml')
def get_last_completed_appointment(patient_id, doctor_id):
    if (current_user.user_id != doctor_id 
        and current_user.account_type.name != 'SuperUser'):
        return USER_NOT_AUTHORIZED(current_user.user_id) 
    return jsonify(last_completed_appointment(patient_id, doctor_id)), 200

@doctor_bp.route('/<int:doctor_id>/discussions', methods=['GET'])
@jwt_required()
@swag_from('../docs/doctor_routes/doctor_general_discussions.yml')
def get_doctor_general_discussions(doctor_id):
    if (current_user.user_id != doctor_id 
        and current_user.account_type.name != 'SuperUser'):
        return USER_NOT_AUTHORIZED(current_user.user_id) 
    return jsonify(doctor_general_discussion(doctor_id)), 200

@doctor_bp.route('/survey/<int:doctor_id>', methods=['POST'])
#@jwt_required()
@swag_from('../docs/doctor_routes/assign_survey_rating.yml')
def assign_survey_rating(doctor_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
   
    patient_id = data.get('patient_id')
    stars = data.get('stars')
    comment = data.get('comment')

    if not patient_id or not stars:
        return jsonify({"error":"patient id and stars are required"})
    try:
        result = assign_survey(doctor_id, patient_id, stars, 
                               comment, requesting_user=current_user)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except NoAuthorizationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(result), 201

@doctor_bp.route('/<int:doctor_id>/appointment_requests', methods=['GET'])
@jwt_required()
@swag_from('../docs/doctor_routes/new_appointment_requests.yml')
def get_new_appointment_requests(doctor_id):
    _acct_type = current_user.account_type.name
    match _acct_type:
        case 'SuperUser':
            pass
        case 'Doctor' if current_user.user_id == doctor_id:
            pass
        case _:
            return USER_NOT_AUTHORIZED(current_user.user_id)
    appointments = new_appointments_request(doctor_id)
    return jsonify(appointments), 200


@doctor_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@swag_from('../docs/doctor_routes/update_doctor_info.yml')
def update_doctor_info(user_id):
    _acct_type = current_user.account_type.name
    match _acct_type:
        case 'SuperUser':
            pass
        case 'Doctor' if current_user.user_id == user_id:
            pass
        case _:
            return USER_NOT_AUTHORIZED(current_user.user_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "no input data provided"}), 400
    try:
        result = update_doctor(user_id, data)
    except ValueError as e:
        return jsonify({
            "error": "invalid fields",
            "fields": e.args[0]}), 400
    except OperationalError as e:
        error_msg = (str(e).split(' ', 1)[1]).partition('\n')[0].split(' ', 1)[1]
        return jsonify({"error": error_msg}), 504
    except IntegrityError as e:
        error_msg = str((str(e.args[0]).split(maxsplit=1))[1]).split(',')[1].strip().strip(')"\\')
        return jsonify({"error": error_msg}), 400
    except Exception as e:
        error_msg = str(e)
        return jsonify({"error": error_msg}), 500
    if "error" not in result:
        return jsonify(result), 200
    return jsonify(result), 404
### ---END PROTECTED ROUTES---


