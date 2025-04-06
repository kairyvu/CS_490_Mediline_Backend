from flaskr.extensions import db

class RatingSurvey(db.Model):
    __tablename__ = 'rating_survey'

    survey_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id'), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    stars = db.Column(db.Integer, nullable=False)

    patient = db.relationship('Patient', backref=db.backref('rating_surveys', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('rating_surveys', lazy=True))