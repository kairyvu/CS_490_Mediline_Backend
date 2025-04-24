from flaskr.models import Chat, Message, Appointment
from flaskr.extensions import db
from datetime import datetime

def get_current_chat(appointment_id):
    chat = Chat.query.filter_by(appointment_id=appointment_id).first()
    if not chat:
        raise ValueError("Chat not found")
    return chat.to_dict()

def add_message(appointment_id, user_id, message_content):
    appointment = Appointment.query.filter_by(appointment_id=appointment_id).first()
    if not appointment:
        return None
    
    chat = Chat.query.filter_by(appointment_id=appointment_id).first()

    if not chat:
        chat = Chat(appointment_id=appointment_id)
        db.session.add(chat)
        db.session.flush()

    message = Message(
        chat_id=chat.chat_id,
        user_id=user_id,
        message_content=message_content,
        time=datetime.now()
    )

    db.session.add(message)
    db.session.commit()

    return {
        "chat_id": chat.chat_id,
        "message_id": message.message_id,
        "user_id": user_id,
        "message": message_content,
        "timestamp": message.time.strftime("%Y-%m-%d %I:%M %p")
    }