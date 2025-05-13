from flask import Blueprint, jsonify, request
from flaskr.services import medication_info, all_meds
from flasgger import swag_from

medication_bp = Blueprint('medication', __name__)

@medication_bp.route('/', methods= ['GET'], strict_slashes=False)
@swag_from('../docs/medication_routes/all_medications.yml')
def all_medications():
    sort_by = request.args.get('sort_by', 'medication_id')
    order = request.args.get('order', 'asc')

    try: 
        result = all_meds(sort_by=sort_by, order=order)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify(result), 200

@medication_bp.route('/<int:medication_id>', methods= ['GET'])
@swag_from('../docs/medication_routes/medication_info.yml')
def medication(medication_id):
    result = medication_info(medication_id)

    if not result:
        return jsonify({"error": "Medication not Found"}), 404
    
    return jsonify(result), 200