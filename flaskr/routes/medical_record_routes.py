from flaskr.services import get_medical_records_by_user
from flask import Blueprint, jsonify
from flasgger import swag_from

medical_record_bp = Blueprint('medical_record', __name__)

@medical_record_bp.route('/<int:user_id>', methods=['GET'])
@swag_from('../docs/medical_record_routes/get_medical_records.yml')
def get_medical_records(user_id):
    try:
        medical_records = get_medical_records_by_user(user_id=user_id)
        return jsonify(medical_records), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medical records'}), 500