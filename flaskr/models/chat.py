from flaskr import db

class Chat(db.Model):
    __tablename__ = 'chat'

    chat_id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'), nullable=False)
    start_date = db.Column(db.DateTime, server_default=db.func.now())
    end_date = db.Column(db.DateTime, nullable=True)
    
    messages = db.relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    appointment = db.relationship('Appointment', backref=db.backref('chat', uselist=False))

    def __init__(self, appointment_id, end_date=None):
        self.appointment_id = appointment_id
        self.end_date = end_date
    
class Message(db.Model):
    __tablename__ = 'message'

    message_id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.chat_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, server_default=db.func.now())

    chat = db.relationship("Chat", back_populates="messages")
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

    def __init__(self, chat_id, user_id, message_content):
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_content = message_content
