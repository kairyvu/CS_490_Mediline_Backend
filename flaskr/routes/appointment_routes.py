from datetime import datetime
from flask import Blueprint, jsonify, request
from flaskr.services import get_upcoming_appointments, add_appointment, update_appointment, get_appointment
from flaskr.struct import AppointmentStatus
from flasgger import swag_from

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/upcoming/<int:user_id>', methods=['GET'])
@swag_from('../docs/appointment_routes/get_all_upcoming_appointments.yml')
def get_all_upcoming_appointments(user_id):
    sort_by = request.args.get('sort_by', 'start_date')
    order = request.args.get('order', 'desc')
    
    try:
        appointments = get_upcoming_appointments(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(appointments), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@appointment_bp.route('/add', methods=['POST'])
@swag_from('../docs/appointment_routes/create_appointment.yml')
def create_appointment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    doctor_id = data.get('doctor_id')
    patient_id = data.get('patient_id')
    treatment = data.get('treatment')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([doctor_id, patient_id, treatment, start_date]):
        return jsonify({"error": "doctor_id, patient_id, treatment, and start_date are required."}), 400
    try:
        start_date_dt = datetime.fromisoformat(start_date)
    except Exception as e:
        return jsonify({"error": f"Invalid start_date format: {e}"}), 400
    end_date_dt = None
    if end_date:
        try:
            end_date_dt = datetime.fromisoformat(end_date)
        except Exception as e:
            return jsonify({"error": f"Invalid end_date format: {e}"}), 400
        if end_date_dt <= start_date_dt:
            return jsonify({"error": "end_date must be after start_date"}), 400

    try:
        appointment_id = add_appointment(doctor_id, patient_id, treatment, start_date, end_date)
        return jsonify(
            {
                "message": "Appointment created successfully",
                "id": appointment_id
            }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@appointment_bp.route('/update/<int:appointment_id>', methods=['PUT'])
@swag_from('../docs/appointment_routes/update_appointment_detail.yml')
def update_appointment_detail(appointment_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    treatment = data.get('treatment')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    status = AppointmentStatus.PENDING
    if data.get('status'):
        status = data.get('status')
    
    if not treatment or not start_date:
        return jsonify({"error": "treatment and start_date are required."}), 400
    try:
        update_appointment(appointment_id, treatment=treatment, start_date=start_date, status=status, end_date=end_date)
        return jsonify({"message": "Appointment updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@appointment_bp.route('/<int:appointment_id>', methods=['GET'])
@swag_from('../docs/appointment_routes/get_appointment_by_id.yml')
def get_appointment_by_id(appointment_id):
    try:
        appointment = get_appointment(appointment_id)
        return jsonify(appointment), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400