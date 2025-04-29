from flask import Blueprint, jsonify, request
from flaskr.services import medication_service
from flasgger import swag_from

medication_bp = Blueprint('medication', __name__)
@medication_bp.route('/<int:medication_id>', methods= ['GET'])
@swag_from('../docs/medication_routes/medication_info.yml')
def medication__info(medication_id):
    result = medication_service.medication_info(medication_id)

    if not result:
        return jsonify({"error": "Medication not Found"}), 404
    
    return jsonify(result), 200