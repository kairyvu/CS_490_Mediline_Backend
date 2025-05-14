from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flaskr.services import get_medical_records_by_user, UnauthorizedError, USER_NOT_AUTHORIZED, create_medical_record, update_medical_record, delete_medical_record
from flasgger import swag_from

medical_record_bp = Blueprint('medical_record', __name__)

@medical_record_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/medical_record_routes/get_medical_records.yml')
def get_medical_records(user_id):
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    try:
        medical_records = get_medical_records_by_user(user_id=user_id, 
                                                      sort_by=sort_by, 
                                                      order=order, 
                                                      requesting_user=current_user)
        return jsonify(medical_records), 200
    except UnauthorizedError:
        return USER_NOT_AUTHORIZED(current_user.user_id)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medical records'}), 500
    
@medical_record_bp.route('/<int:patient_id>/medical_history', methods=['POST'])
#@jwt_required()
@swag_from('../docs/medical_record_routes/insert_medical_record.yml')
def insert_medical_record(patient_id):
    """
    _is_su = current_user.account_type.name == 'SuperUser'
    _is_self = current_user.user_id == patient_id
    _is_doc = ((current_user.account_type.name == 'Doctor')
               and (patient_id in (p.user_id for p in current_user.doctor.patients)))
    if (not _is_su) or (not _is_self) or (not _is_doc):
        return USER_NOT_AUTHORIZED(current_user.user_id)
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "no input data provided"}), 400
    
    description = data.get("description")
    appointment_id = data.get("appointment_id")
    if not appointment_id:
        return jsonify({"error": "Appointment id is required"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    result = create_medical_record(appointment_id, patient_id, description)
    if result is None:
        return jsonify({"error": "Appointment not found"}), 404
    
    return jsonify(result), 201


@medical_record_bp.route('/<int:medical_record_id>', methods=['PUT'])
@swag_from('../docs/medical_record_routes/update_medical_record.yml')
def update_medical_record_route(medical_record_id):
    data = request.get_json()
    description = data.get('description')
    if not description:
        return jsonify({"error": "Description is required"}), 400
    
    result = update_medical_record(medical_record_id, description)
    if result is None:
        return jsonify({"error": "Medical record not found"}), 404
    return jsonify(result), 200


@medical_record_bp.route('/<int:medical_record_id>', methods=['DELETE'])
@swag_from('../docs/medical_record_routes/delete_medical_record.yml')
def delete_medical_record_route(medical_record_id):
    result = delete_medical_record(medical_record_id)
    if result is None:
        return jsonify({"error": "Medical record not found"}), 404
    return jsonify(result), 200   
