from flask import Blueprint, jsonify, request
from flaskr.services import patient_service
from flasgger import swag_from

from sqlalchemy.exc import OperationalError, IntegrityError

patient_bp = Blueprint('patient_bp', __name__, url_prefix='/patients')

@patient_bp.route('/<int:user_id>/info', methods=['GET'])
@swag_from('../docs/patient_routes/get_patient_info.yml')
def get_patient_info(user_id):
    result = patient_service.get_patient_info(user_id)
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
        result = patient_service.update_patient(user_id, data)
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