from flask import Blueprint, jsonify, request
from flaskr.services import get_medications_by_prescription, get_prescriptions, get_prescription_count_by_pharmacy, get_pharmacy_medications_inventory, get_medications_history_by_patient, update_prescription_status
from flasgger import swag_from

prescription_bp = Blueprint("prescription", __name__)
@prescription_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from('../docs/prescription_routes/get_prescription_by_user.yml')
def get_prescription_by_user(user_id):
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'asc')

    try:
        prescriptions = get_prescriptions(user_id=user_id, sort_by=sort_by, order=order)
        return jsonify(prescriptions), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@prescription_bp.route('/<int:prescription_id>/medications', methods=['GET'])
@swag_from('../docs/prescription_routes/get_medication_list.yml')
def get_medication_list(prescription_id):
    try:
        medications = get_medications_by_prescription(prescription_id)
        return jsonify(medications), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medications'}), 500

## TODO: Documentation
@prescription_bp.route('/pharmacy/<int:pharmacy_id>/count', methods=['GET'])
def get_prescription_count(pharmacy_id):
    try:
        count = get_prescription_count_by_pharmacy(pharmacy_id)
        return jsonify(count), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the prescription count'}), 500

## TODO: Documentation
@prescription_bp.route('/pharmacy/<int:pharmacy_id>/inventory', methods=['GET'])
def get_pharmacy_inventory(pharmacy_id):
    try:
        inventory = get_pharmacy_medications_inventory(pharmacy_id)
        return jsonify(inventory), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the pharmacy inventory'}), 500
    
## TODO: Documentation
@prescription_bp.route('/patient/<int:patient_id>/history', methods=['GET'])
def get_medications_history(patient_id):
    try:
        history = get_medications_history_by_patient(patient_id)
        return jsonify(history), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the medications history'}), 500

@prescription_bp.route('/<int:prescription_id>', methods=['PATCH'])
@swag_from('../docs/prescription_routes/update_prescription_status.yml')
def update_prescription(prescription_id):
    data = request.get_json()
    status = data.get('status')
    try:
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        updated_prescription = update_prescription_status(prescription_id, status)
        return jsonify(updated_prescription), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred while updating the prescription'}), 500