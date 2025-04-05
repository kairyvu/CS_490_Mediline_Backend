from flaskr import db
import enum

class PaymentStatus(enum.Enum):
    PAID = 'paid'
    PENDING = 'pending'

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

class PaymentPrescription(db.Model):
    __tablename__ = 'payment_prescription'

    payment_prescription_id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.prescription_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    prescription = db.relationship('Prescription', backref=db.backref('payment_prescriptions', lazy=True))
    invoice = db.relationship('Invoice', backref=db.backref('payment_prescriptions', lazy=True))

    def __init__(self, prescription_id, amount):
        self.prescription_id = prescription_id
        self.amount = amount