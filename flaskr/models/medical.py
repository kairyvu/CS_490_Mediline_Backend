from flaskr.extensions import db

class MedicalRecord(db.Model):
    __tablename__ = 'medical_record'

    medical_record_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    patient = db.relationship('Patient', backref=db.backref('medical_records', lazy=True))

class Prescription(db.Model):
    __tablename__ = 'prescription'

    prescription_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    patient = db.relationship('Patient', backref=db.backref('prescriptions', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('prescriptions', lazy=True))

class PrescriptionMedication(db.Model):
    __tablename__ = 'prescription_medication'

    prescription_medication_id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.prescription_id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.medication_id'), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    medical_instructions = db.Column(db.Text, nullable=False)

class Medication(db.Model):
    __tablename__ = 'medication'

    medication_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Inventory(db.Model):
    __tablename__ = 'inventory'

    inventory_id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.user_id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.medication_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    pharmacy = db.relationship('Pharmacy', backref=db.backref('inventories', lazy=True))
    medication = db.relationship('Medication', backref=db.backref('inventories', lazy=True))