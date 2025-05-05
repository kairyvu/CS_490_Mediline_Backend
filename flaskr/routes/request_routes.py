from flask import Blueprint, jsonify, request
from flaskr.services import add_patient_request, delete_patient_request, get_patient_requests_by_doctor_id
from flasgger import swag_from

request_bp = Blueprint("request", __name__)

@request_bp.route('/<int:patient_id>:<int:doctor_id>', methods=['POST'])
@swag_from('../docs/request_routes/add_request.yml')
def add_request(patient_id, doctor_id):
    try:
        request_data = add_patient_request(patient_id, doctor_id)
        return jsonify(request_data), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@request_bp.route('/<int:request_id>', methods=['DELETE'])
@swag_from('../docs/request_routes/delete_request.yml')
def delete_request(request_id):
    try:
        request_data = delete_patient_request(request_id)
        if request_data is None:
            return jsonify({"error": "Request not found"}), 404
        return jsonify(request_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@request_bp.route('/<int:doctor_id>', methods=['GET'])
@swag_from('../docs/request_routes/get_request_by_doctor_id.yml')
def get_request_by_doctor_id(doctor_id, sort_by='created_at', order='desc'):
    sort_by = request.args.get('sort_by', sort_by)
    order = request.args.get('order', order)

    try:
        requests = get_patient_requests_by_doctor_id(doctor_id, sort_by=sort_by, order=order)
        return jsonify(requests), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500