from flask import Blueprint, Flask
from .database import database_bp
from .register import register_bp

main_bp = Blueprint('main', __name__)

def register_routes(app: Flask):
    app.register_blueprint(database_bp, url_prefix='/test_connection')
    app.register_blueprint(register_bp, url_prefix='/register')