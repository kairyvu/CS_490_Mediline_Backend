from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flaskr.models import User
from flaskr.services import get_invoices_by_user, update_invoice_status, assign_invoice_appoinmtnet, delete_invoice, USER_NOT_AUTHORIZED
from flasgger import swag_from

payment_bp = Blueprint("payment", __name__)

@payment_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/payment_routes/get_invoices_by_user_route.yml')
def get_invoices_by_user_route(user_id):
    _user: User = current_user
    _user_id = _user.user_id
    _acct_type = _user.account_type.name
    match _acct_type:
        case 'SUPERUSER' | 'PATIENT' if _user_id == user_id:
            pass
        case _:
            return USER_NOT_AUTHORIZED(_user_id)
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    try:
        invoices = get_invoices_by_user(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(invoices), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@payment_bp.route('/patient/<int:patient_id>/invoice/<int:invoice_id>', methods=['PUT'])
@jwt_required()
@swag_from('../docs/payment_routes/update_invoice_status.yml')
def update_invoice_status_put(patient_id, invoice_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "no input data provided"}), 400
    if ((current_user.account_type.name != 'SUPERUSER') 
        and (current_user.user_id != patient_id)):
        return USER_NOT_AUTHORIZED(current_user.user_id)
    
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400
    
    result = update_invoice_status(patient_id, invoice_id, new_status)
    if not result:
        return jsonify({"error": "Invoice Not Found"}), 404
    return jsonify(result), 200

@payment_bp.route('/', methods=['POST'])
@jwt_required()
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

    return assign_invoice_appoinmtnet(doctor_id, appointment_id, patient_id, requesting_user=current_user)

@payment_bp.route('/invoice/<int:invoice_id>', methods=['DELETE'])
@jwt_required()
@swag_from('../docs/payment_routes/delete_invoice.yml')
def delete_invoices(invoice_id):
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    if ((current_user.account_type.name != 'SUPERUSER') 
        and (current_user.user_id != doctor_id)):
        return USER_NOT_AUTHORIZED(current_user.user_id)
    
    result = delete_invoice(doctor_id, invoice_id)
    
    if not result:
        return jsonify ({"error": "Invoice not found or not authorized"}), 404
    return jsonify(result), 200
