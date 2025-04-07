from flask import Blueprint, jsonify, request
from flaskr.services import get_upcoming_appointments

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/upcoming/<int:user_id>', methods=['GET'])
def get_all_upcoming_appointments(user_id):
    sort_by = request.args.get('sort_by', 'start_date')
    order = request.args.get('order', 'desc')
    
    try:
        appointments = get_upcoming_appointments(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(appointments), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400