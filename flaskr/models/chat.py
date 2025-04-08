from flaskr.extensions import db

class Chat(db.Model):
    __tablename__ = 'chat'

    chat_id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'), nullable=False)
    start_date = db.Column(db.DateTime, server_default=db.func.now())
    end_date = db.Column(db.DateTime, nullable=True)
    
    messages = db.relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.time.asc()")
    appointment = db.relationship('Appointment', backref=db.backref('chat', uselist=False))

    def to_dict(self):
        return {
            'chat_id': self.chat_id,
            'appointment_id': self.appointment_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'messages': [message.to_dict() for message in self.messages]
        }
    
class Message(db.Model):
    __tablename__ = 'message'

    message_id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.chat_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, server_default=db.func.now())

    chat = db.relationship("Chat", back_populates="messages")
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

    def to_dict(self):
        return {
            'message_id': self.message_id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'message_content': self.message_content,
            'time': self.time.isoformat()
        }
