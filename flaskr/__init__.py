from flask import Flask
from flaskr.routes import register_routes

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    register_routes(app)
    return app