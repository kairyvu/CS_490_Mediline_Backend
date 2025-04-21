from flask import Blueprint, jsonify, request
from flaskr.services import get_all_pharmacy_patients
from flasgger import swag_from

pharmacy_bp = Blueprint('pharmacy', __name__)
@pharmacy_bp.route('/<int:pharmacy_id>/patients', methods=['GET'])
@swag_from('../docs/pharmacy_routes/get_pharmacy_patients.yml')
def get_pharmacy_patients(pharmacy_id):
    try:
        history = get_all_pharmacy_patients(pharmacy_id=pharmacy_id)
        return jsonify(history), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medications history'}), 500