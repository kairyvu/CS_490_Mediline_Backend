from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from flaskr.cli import register_commands
from flaskr.extensions import db


    
load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    username = os.getenv("DB_USER") or os.getenv("MYSQL_USER")
    password = os.getenv("DB_PASS") or os.getenv("MYSQL_PASSWORD")
    host = os.getenv("DB_HOST") or os.getenv("MYSQL_HOST")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME", "doctor_patient_system")
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
    app.config['SWAGGER'] = {
        'doc_dir': './docs/' 
    }

    db.init_app(app)
    migrate = Migrate(app, db)
    from flaskr.extensions import swag
    swag.init_app(app)
    
    from flaskr.routes import register_routes
    register_routes(app)
    register_commands(app)

    return app
