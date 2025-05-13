from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from flask_socketio import emit, join_room, rooms, send
from flaskr.services import get_current_chat, add_message, USER_NOT_AUTHORIZED, UnauthorizedError
from flaskr.extensions import sio
from flasgger import swag_from

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/chat_routes/get_chat.yml')
def get_chat(appointment_id):
    try:
        chat = get_current_chat(appointment_id, requesting_user=current_user)
        return jsonify(chat), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except UnauthorizedError as e:
        return USER_NOT_AUTHORIZED(current_user.user_id)
    

@chat_bp.route('/appointment/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@swag_from('../docs/chat_routes/put_message.yml')
def put_message(appointment_id):
    data = request.get_json()
    user_id = data.get("user_id")
    message_content = data.get("message")
    appointment_id = data.get("appointment_id")

    if not user_id or not message_content or not appointment_id:
        return jsonify({"error": "user id and message and appointment id are required"}), 400

    result = add_message(appointment_id, user_id, message_content)
    if result is None:
        return jsonify({"error": "Invalid appointment id"}), 404

    return jsonify(result), 201

# Socket IO
@sio.event(namespace='/chat')
def connect():
    emit('Connected to chat')

@sio.on('join', namespace='/chat')
def handle_join(data):
    # Expecting json payload with appointment id
    room = data['appointment_id']
    join_room(room)

@sio.on('message', namespace='/chat')
def handle_message(data):
    # Expecting json payload with:
    # appointment_id, user_id, message content
    emit('message', {
        'user_id': data['user_id'], 
        'message': data['message'], 
        'timestamp': datetime.now(tz=timezone.utc)
    }, namespace='/chat', to=data['appointment_id'])

    add_message(data['appointment_id'], data['user_id'], data['message'])