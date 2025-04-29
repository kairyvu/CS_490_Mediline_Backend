from flask import Blueprint, jsonify, request
from flaskr.services import get_invoices_by_user, update_invoice_status, assign_invoice_appoinmtnet
from flasgger import swag_from

payment_bp = Blueprint("payment", __name__)

@payment_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from('../docs/payment_routes/get_invoices_by_user_route.yml')
def get_invoices_by_user_route(user_id):
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    try:
        invoices = get_invoices_by_user(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(invoices), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@payment_bp.route('/patient/<int:patient_id>/invoice/<int:invoice_id>', methods=['PUT'])
@swag_from('../docs/payment_routes/update_invoice_status.yml')
def update_invoice_status_put(patient_id, invoice_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "no input data provided"}), 400
    
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
    
    result = update_invoice_status(patient_id, invoice_id, new_status)
    if not result:
        return jsonify({"error": "Invoice Not Found"}), 404
    return jsonify(result), 200

@payment_bp.route('/', methods=['POST'])
@swag_from('../docs/payment_routes/assign_invoice.yml')
def assign_invoice():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    appointment_id = data.get('appointment_id')
    patient_id = data.get('patient_id')

    if not doctor_id:
        return jsonify({"error": "Missing Doctor ID"}), 400
    if not patient_id:
        return jsonify({"error": "Missing Patient ID"}), 400
    if not appointment_id:
        return jsonify({"error": "Missing Appointment ID"}), 400
    result = assign_invoice_appoinmtnet(doctor_id, appointment_id, patient_id)

    if not result:
        return jsonify({"error": "appointment not found"}), 404

    return jsonify(result), 200