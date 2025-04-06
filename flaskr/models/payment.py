from flaskr import db
from flaskr.struct import PaymentStatus

class Invoice(db.Model):
    __tablename__ = 'invoice'

    invoice_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id'), nullable=False)
    status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    pay_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    patient = db.relationship('Patient', backref=db.backref('invoices', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('invoices', lazy=True))

    def __init__(self, patient_id, doctor_id, status=PaymentStatus.PENDING, pay_date=None):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.status = status
        self.pay_date = pay_date
