from flaskr.models import Chat
from flaskr.extensions import db

def get_current_chat(appointment_id):
    chat = Chat.query.filter_by(chat_id=appointment_id).first()
    if not chat:
        raise ValueError("Chat not found")
    return chat.to_dict()