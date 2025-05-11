from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flaskr.models import User, Patient
from flaskr.services import get_patient_report_result, add_patient_report, get_latest_report_by_user, USER_NOT_AUTHORIZED
from flasgger import swag_from

report_bp = Blueprint("report", __name__)

@report_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/report_routes/get_report_by_user.yml')
def get_report_by_user(user_id):
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
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'asc')

    try:
        reports = get_patient_report_result(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(reports), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@report_bp.route('/user/<int:user_id>', methods=['POST'])
@jwt_required()
@swag_from('../docs/report_routes/add_report.yml')
def add_report(user_id):
    _user_id = current_user.user_id
    _acct_type = current_user.account_type.name
    if (_user_id != user_id) and (_acct_type != 'SuperUser'):
        return USER_NOT_AUTHORIZED(_user_id)

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

    fields = [report_id, doctor_id, height, weight,
            calories_intake, hours_of_exercise, hours_of_sleep]
    if any(f is None for f in fields):
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
    
@report_bp.route('/user/<int:user_id>/latest', methods=['GET'])
@jwt_required()
@swag_from('../docs/report_routes/get_latest_report.yml')
def get_latest_report(user_id):
    _user_id = current_user.user_id
    _acct_type = current_user.account_type.name
    if _acct_type == 'SuperUser' or _user_id == user_id:
        pass
    elif _acct_type == 'Pharmacy':
        belongs = Patient.query.filter_by(user_id=user_id, pharmacy_id=_user_id).first()
        if not belongs:
            return USER_NOT_AUTHORIZED(_user_id)
    elif _acct_type == 'Doctor':
        belongs = Patient.query.filter_by(user_id=user_id, doctor_id=_user_id).first()
        if not belongs:
            return USER_NOT_AUTHORIZED(_user_id)
    else:
        return USER_NOT_AUTHORIZED(_user_id)
    try:
        report = get_latest_report_by_user(user_id=user_id)
        return jsonify(report), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400