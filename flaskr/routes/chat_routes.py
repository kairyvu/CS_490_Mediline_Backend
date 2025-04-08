from flask import Blueprint, jsonify, request
from flaskr.services import get_current_chat

chat_bp = Blueprint('chat', __name__)
@chat_bp.route('/<int:appointment_id>', methods=['GET'])
def get_chat(appointment_id):
    try:
        chat = get_current_chat(appointment_id)
        return jsonify(chat), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400