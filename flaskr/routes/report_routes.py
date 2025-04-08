from flask import Blueprint, jsonify, request
from flaskr.services import get_patient_report_result, add_patient_report

report_bp = Blueprint("report", __name__)
@report_bp.route('/user/<int:user_id>', methods=['GET'])
def get_report_by_user(user_id):
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'asc')

    try:
        reports = get_patient_report_result(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(reports), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@report_bp.route('/user/<int:user_id>', methods=['POST'])
def add_report(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    report_id = data.get('report_id')
    doctor_id = data.get('doctor_id')
    height = data.get('height')
    weight = data.get('weight')
    calories_intake = data.get('calories_intake')
    hours_of_exercise = data.get('hours_of_exercise')
    hours_of_sleep = data.get('hours_of_sleep')

    if not all([report_id, doctor_id, height, weight, calories_intake, hours_of_exercise, hours_of_sleep]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        add_patient_report(report_id=report_id, patient_id=user_id, doctor_id=doctor_id,
                           height=height, weight=weight,
                           calories_intake=calories_intake,
                           hours_of_exercise=hours_of_exercise,
                           hours_of_sleep=hours_of_sleep)
        return jsonify({"message": "Report added successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400