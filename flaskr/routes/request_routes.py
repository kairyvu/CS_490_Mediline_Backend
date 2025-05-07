from flask import Blueprint, jsonify, request
from flaskr.services import add_patient_request, delete_patient_request, get_patient_requests_by_doctor_id, update_doctor_by_patient_id
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
    data = request.get_json()
    if data and 'status' in data:
        status = data.get('status')
        if status not in ['accepted', 'rejected']:
            return jsonify({"error": "Invalid status"}), 400
        if status == 'accepted':
            try:
                request_data = delete_patient_request(request_id)
                if request_data is None:
                    return jsonify({"error": "Request not found"}), 404
                patient = update_doctor_by_patient_id(patient_id=request_data['patient_id'], doctor_id=request_data['doctor_id'])
                if patient is None:
                    return jsonify({"error": "Patient not found"}), 404
                return jsonify({"message": "Request accepted", "patient": patient}), 200
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        elif status == 'rejected':
            try:
                request_data = delete_patient_request(request_id)
                if request_data is None:
                    return jsonify({"error": "Request not found"}), 404
                return jsonify({"message": "Request rejected", "request": request_data}), 200
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        
    return jsonify({"error": "Invalid request"}), 400

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