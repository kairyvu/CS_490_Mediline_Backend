from flaskr import db

class MedicalRecord(db.Model):
    __tablename__ = 'medical_record'

    medical_record_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    patient = db.relationship('Patient', backref=db.backref('medical_records', lazy=True))

    def __init__(self, patient_id, description):
        self.patient_id = patient_id
        self.description = description

class Prescription(db.Model):
    __tablename__ = 'prescription'

    prescription_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.user_id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    patient = db.relationship('Patient', backref=db.backref('prescriptions', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('prescriptions', lazy=True))

    def __init__(self, patient_id, doctor_id):
        self.patient_id = patient_id
        self.doctor_id = doctor_id

class PrescriptionMedication(db.Model):
    __tablename__ = 'prescription_medication'

    prescription_medication_id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.prescription_id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.medication_id'), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    medical_instructions = db.Column(db.Text, nullable=False)

    def __init__(self, prescription_id, medication_id, dosage, medical_instructions):
        self.prescription_id = prescription_id
        self.medication_id = medication_id
        self.dosage = dosage
        self.medical_instructions = medical_instructions

class Medication(db.Model):
    __tablename__ = 'medication'

    medication_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description

class Inventory(db.Model):
    __tablename__ = 'inventory'

    inventory_id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.user_id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.medication_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    pharmacy = db.relationship('Pharmacy', backref=db.backref('inventories', lazy=True))
    medication = db.relationship('Medication', backref=db.backref('inventories', lazy=True))

    def __init__(self, pharmacy_id, medication_id, quantity=0):
        self.pharmacy_id = pharmacy_id
        self.medication_id = medication_id
        self.quantity = quantity