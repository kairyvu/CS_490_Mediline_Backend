from flaskr.extensions import db

class Notification(db.Model):
    __tablename__ = 'notification'

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    notification_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def to_dict(self):
        return {
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "notification_content": self.notification_content,
            "created_at": self.created_at.isoformat()
        }