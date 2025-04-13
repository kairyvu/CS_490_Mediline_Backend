"""\
    Address model relating to Users
"""
from flaskr.extensions import db
            
class Address(db.Model):
    __tablename__ = 'address'
    
    address_id  = db.Column(db.Integer, primary_key=True)
    address1    = db.Column(db.String(128), nullable=False)
    address2    = db.Column(db.String(128), nullable=False)
    city_id     = db.Column(db.Integer, db.ForeignKey('city.city_id'), nullable=False)
    state       = db.Column(db.String(128), nullable=False)
    zipcode     = db.Column(db.String(20), nullable=False)
    created_at  = db.Column(db.DateTime, server_default=db.func.now())
    updated_at  = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            "address_id": self.address_id,
            "address1": self.address1,
            "address2": self.address2,
            "city_id": self.city_id,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class City(db.Model):
    __tablename__ = 'city'

    city_id     = db.Column(db.Integer, primary_key=True)
    city        = db.Column(db.String(80), nullable=False, default='NULL')
    country_id  = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=False)
    created_at  = db.Column(db.DateTime, server_default=db.func.now())
    updated_at  = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    addresses = db.relationship('Address', backref=db.backref('city', lazy=True))

class Country(db.Model):
    __tablename__ = 'country'

    country_id  = db.Column(db.Integer, primary_key=True)
    country     = db.Column(db.String(80), nullable=False, unique=True, default='NULL')
    created_at  = db.Column(db.DateTime, server_default=db.func.now())
    updated_at  = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    cities = db.relationship('City', backref=db.backref('country', lazy=True))