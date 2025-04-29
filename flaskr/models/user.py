#from datetime 
from werkzeug.security import generate_password_hash, check_password_hash
from flaskr.extensions import db
from flaskr.struct import AccountType


class User(db.Model):
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))

    account_type = db.Column(db.Enum(AccountType), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    address = db.relationship('Address', backref=db.backref('user', lazy=True))

    def __init__(self, username, password, account_type, address_id):
        self.username = username
        self.password = generate_password_hash(password)
        self.account_type = account_type \
            if isinstance(account_type, AccountType) \
            else AccountType(account_type)
        self.address_id = address_id

    @classmethod
    def authenticate(cls, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')

        if not (username and password):
            return None
        
        user = cls.query.filter_by(username=username).first()
        if not (user and check_password_hash(user.password, password)):
            return None
        
        return user

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "account_type": self.account_type.value if isinstance(self.account_type, AccountType) else self.account_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class SuperUser(db.Model):
    __tablename__ = 'super_user'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('super_user', uselist=False))

    def to_dict(self):
        return {
            "user_id": self.user_id
        }
    
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

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "specialization": self.specialization,
            "bio": self.bio,
            "fee": self.fee,
            "profile_picture": self.profile_picture,
            "dob": self.dob.isoformat() if self.dob else None,
            "license_id": self.license_id
        }
    
class Pharmacy(db.Model):
    __tablename__ = 'pharmacy'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True, nullable=False)
    pharmacy_name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hours = db.Column(db.String(80), nullable=False)
    
    user = db.relationship('User', backref=db.backref('pharmacy', uselist=False))

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "pharmacy_name": self.pharmacy_name,
            "phone": self.phone,
            "email": self.email,
            "hours": self.hours,
        }


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