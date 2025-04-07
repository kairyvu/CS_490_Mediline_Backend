from flask import Blueprint, Flask
from .database import database_bp
from .auth_routes import auth_bp
from .patient_routes import patient_bp


from .doctor_routes import doctor_bp

main_bp = Blueprint('main', __name__)

def register_routes(app: Flask):
    app.register_blueprint(database_bp, url_prefix='/test_connection')
    
    app.register_blueprint(doctor_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)