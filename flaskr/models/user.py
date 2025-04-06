from flaskr.extensions import db
from flaskr.struct import AccountType

class User(db.Model):
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

class SuperUser(db.Model):
    __tablename__ = 'super_user'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('super_user', uselist=False))
    
class Doctor(db.Model):
    __tablename__ = 'doctor'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    specialization = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    fee = db.Column(db.Float, nullable=False)
    profile_picture = db.Column(db.String(120), nullable=True)
    dob = db.Column(db.Date, nullable=False)
    license_id = db.Column(db.String(80), unique=True, nullable=False)
    
    user = db.relationship('User', backref=db.backref('doctor', uselist=False))
    
class Pharmacy(db.Model):
    __tablename__ = 'pharmacy'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True, nullable=False)
    pharmacy_name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hours = db.Column(db.String(80), nullable=False)
    zipcode = db.Column(db.String(20), nullable=False)
    
    user = db.relationship('User', backref=db.backref('pharmacy', uselist=False))


class Patient(db.Model):
    __tablename__ = 'patient'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.user_id'), nullable=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.user_id'), nullable=True)
    
    user = db.relationship('User', backref=db.backref('patient', uselist=False))
    doctor = db.relationship('Doctor', backref=db.backref('patients', lazy=True))
    pharmacy = db.relationship('Pharmacy', backref=db.backref('patients', lazy=True))
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "dob": self.dob.isoformat() if self.dob else None,
            "email": self.email,
            "phone": self.phone,
            "doctor_id": self.doctor_id,
            "pharmacy_id": self.pharmacy_id
        }