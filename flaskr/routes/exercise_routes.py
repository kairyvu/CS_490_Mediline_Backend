from flask import Blueprint, jsonify, request
from flaskr.services import get_exercises, get_all_patient_exercise, add_patient_exercise, update_patient_exercise

exercise_bp = Blueprint("exercise", __name__)

@exercise_bp.route('/', methods=['GET'])
def get_all_exercises():
    sort_by = request.args.get('sort_by', 'exercise_id')
    order = request.args.get('order', 'asc')
    
    try:
        exercise = get_exercises(sort_by=sort_by, order=order)
        return jsonify(exercise), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@exercise_bp.route('/user/<int:user_id>', methods=['GET'])
def get_exercise_by_user(user_id):
    sort_by = request.args.get('sort_by', 'exercise_id')
    order = request.args.get('order', 'asc')
    
    try:
        exercise = get_all_patient_exercise(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(exercise), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@exercise_bp.route('/<int:exercise_id>', methods=['POST'])
def add_exercise(exercise_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    reps = data.get('reps')
    
    if not all([patient_id, doctor_id, reps]):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        add_patient_exercise(exercise_id=exercise_id, patient_id=patient_id, doctor_id=doctor_id, reps=reps)
        return jsonify({"message": "Exercise added successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@exercise_bp.route('/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    status = data.get('status')
    reps = data.get('reps')
    if not status or not reps:
        return jsonify({"error": "status and reps are required"}), 400
    try:
        update_patient_exercise(exercise_id=exercise_id, status=status, reps=reps)
        return jsonify({"message": "Exercise updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400