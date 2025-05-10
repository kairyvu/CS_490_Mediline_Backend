from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flaskr.models import User
from flaskr.services import get_exercises, get_all_patient_exercise, \
    add_patient_exercise, update_patient_exercise, USER_NOT_AUTHORIZED, \
    UnauthorizedError
from flasgger import swag_from

from sqlalchemy.exc import IntegrityError   # For exception handling (foreign key constraint failure)

exercise_bp = Blueprint("exercise", __name__)

### ---PUBLIC ROUTES---
@exercise_bp.route('/', methods=['GET'])
@swag_from('../docs/exercise_routes/get_all_exercises.yml')
def get_all_exercises():
    sort_by = request.args.get('sort_by', 'exercise_id')
    order = request.args.get('order', 'asc')
    
    try:
        exercise = get_exercises(sort_by=sort_by, order=order)
        return jsonify(exercise), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
### ---END PUBLIC ROUTES---

### ---PROTECTED ROUTES---
@exercise_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/exercise_routes/get_exercise_by_user.yml')
def get_exercise_by_user(user_id):
    _user: User = current_user
    _user_id = _user.user_id
    _acct_type = _user.account_type.name
    match _acct_type:
        case 'SuperUser':
            pass
        case 'Patient' if _user_id == user_id:
            pass
        case 'Doctor' if user_id in set([
            p.user_id for p in _user.doctor.patients]):
            pass
        case _:
            return USER_NOT_AUTHORIZED(_user_id)
    sort_by = request.args.get('sort_by', 'exercise_id')
    order = request.args.get('order', 'asc')
    
    try:
        exercise = get_all_patient_exercise(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(exercise), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@exercise_bp.route('/<int:exercise_id>', methods=['POST'])
@jwt_required()
@swag_from('../docs/exercise_routes/add_exercise.yml')
def add_exercise(exercise_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    reps = data.get('reps')
    _user: User = current_user
    _user_id = _user.user_id
    _acct_type = _user.account_type.name
    match _user_id, _acct_type:
        case 'SuperUser':
            pass
        case 'Doctor' if ((doctor_id == _user_id) 
            and patient_id in set([p.user_id for p in _user.doctor.patients])):
            # Doctor who is assigned a patient can edit that patient's exercises
            pass
        case 'Patient' if patient_id == _user_id:
            # Patient can assign their own exercise
            pass
        case _:
            return USER_NOT_AUTHORIZED(_user_id)
    
    if not all([patient_id, doctor_id, reps]):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        patient_exercise_id = add_patient_exercise(exercise_id=exercise_id, patient_id=patient_id, doctor_id=doctor_id, reps=reps)
        return jsonify(
            {
                "message": "Exercise added successfully",
                "id": patient_exercise_id
            }), 201
    except IntegrityError as e:
        # Possible integrity error: foreign key failure (i.e. exercise in exercise_bank with `exercise_id`` does not exist)
        error_msg = ''.join((str(e.args[0]).split(maxsplit=1)[1]).split(',')[1:]).lstrip().strip("'")
        return jsonify({'error': f'{error_msg}'}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@exercise_bp.route('/<int:exercise_id>', methods=['PUT'])
@jwt_required()
@swag_from('../docs/exercise_routes/update_exercise.yml')
def update_exercise(exercise_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    status = data.get('status')
    reps = data.get('reps')
    if not status or not reps:
        return jsonify({"error": "status and reps are required"}), 400
    try:
        update_patient_exercise(exercise_id=exercise_id, status=status, 
                                reps=reps, requesting_user=current_user)
        return jsonify({"message": "Exercise updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except UnauthorizedError as e:
        return USER_NOT_AUTHORIZED(current_user.user_id)
### ---END PROTECTED ROUTES---