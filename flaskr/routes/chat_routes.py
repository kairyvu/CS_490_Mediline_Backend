from flask import Blueprint, jsonify, request
from flaskr.services import get_current_chat, chat_service
from flasgger import swag_from

chat_bp = Blueprint('chat', __name__)
@chat_bp.route('/<int:appointment_id>', methods=['GET'])
@swag_from('../docs/chat_routes/get_chat.yml')
def get_chat(appointment_id):
    try:
        chat = get_current_chat(appointment_id)
        return jsonify(chat), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    

@chat_bp.route('/appointment/<int:appointment_id>', methods=['PUT'])
def put_message(appointment_id):
    data = request.get_json()
    user_id = data.get("user_id")
    message_content = data.get("message")
    appointment_id = data.get("appointment_id")

    if not user_id or not message_content or not appointment_id:
        return jsonify({"error": "user id and message and appointment id are required"}), 400

    result = chat_service.add_message(appointment_id, user_id, message_content)
    if result is None:
        return jsonify({"error": "Invalid appointment id"}), 404

    return jsonify(result), 201
