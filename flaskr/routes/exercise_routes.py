from flask import Blueprint, jsonify, request
from flaskr.services import get_exercises, get_user_exercise

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
        exercise = get_user_exercise(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(exercise), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400