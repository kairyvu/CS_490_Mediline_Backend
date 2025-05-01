from flask import Blueprint, jsonify, request
from flaskr.services import get_patient_info, update_patient, patient_medical_history, create_medical_record, update_primary_pharmacy
from flasgger import swag_from

from sqlalchemy.exc import OperationalError, IntegrityError

patient_bp = Blueprint('patient_bp', __name__)

@patient_bp.route('/<int:user_id>/info', methods=['GET'])
@swag_from('../docs/patient_routes/get_patient_info.yml')
def get_patient_info(user_id):
    result = get_patient_info(user_id)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Patient not found"}), 404

@patient_bp.route('/<int:user_id>', methods=['PUT'])
@swag_from('../docs/patient_routes/update_patient_info.yml')
def update_patient_info(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "no input data provided"}), 400
    try:
        result = update_patient(user_id, data)
    except ValueError as e:
        return jsonify({
            "error": "invalid fields",
            "fields": e.args[0]}), 400
    except OperationalError as e:
        error_msg = (str(e).split(' ', 1)[1]).partition('\n')[0].split(' ', 1)[1]
        return jsonify({"error": error_msg}), 504
    except IntegrityError as e:
        error_msg = str((str(e.args[0]).split(maxsplit=1))[1]).split(',')[1].strip().strip(')"\\')
        return jsonify({"error", error_msg}), 400
    if "error" not in result:
        return jsonify(result), 200
    return jsonify(result), 404

@patient_bp.route('/<int:patient_id>/medical_history', methods=['GET'])
@swag_from('../docs/patient_routes/medical_history.yml')
def medical_history(patient_id):
    result = patient_medical_history(patient_id)
    if not result:
        return jsonify({"error": "Patient not Found"}), 404
    return jsonify(result), 200

@patient_bp.route('/<int:patient_id>/medical_history', methods=['POST'])
@swag_from('../docs/patient_routes/insert_medical_record.yml')
def insert_medical_record(patient_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "no input data provided"}), 400
    
    description = data.get("description")
    if not description:
        return jsonify({"error": "Description is required"}), 400
    result = create_medical_record(patient_id, description)
    if result is None:
        return jsonify({"error": "Patient not found"}), 404
    
    return jsonify(result), 201

@patient_bp.route('/<int:patient_id>/pharmacy', methods=['PUT'])
@swag_from('../docs/patient_routes/update_primary_pharmacy.yml')
def primary_pharmacy(patient_id):
    data = request.get_json()
    pharmacy_id = data.get("pharmacy_id")
    if not pharmacy_id:
        return jsonify({"error": "Pharmacy ID is required"}), 400

    result = update_primary_pharmacy(patient_id, pharmacy_id)
    if result == "Patient not found":
        return jsonify({"error": "Patient not found"}), 404
    elif result == "Pharmacy not found":
        return jsonify({"error": "Pharmacy not found"}), 404
    else:
        return jsonify(result), 200
    

    
