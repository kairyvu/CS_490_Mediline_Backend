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
    host = os.getenv("INSTANCE_HOST") or os.getenv("MYSQL_HOST")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME", "doctor_patient_system")

    connect_args = {}
    # For deployments that connect directly to a Cloud SQL instance without
    # using the Cloud SQL Proxy, configuring SSL certificates will ensure the
    # connection is encrypted.
    if os.environ.get("DB_ROOT_CERT"):
        db_root_cert = os.environ["DB_ROOT_CERT"]
        db_cert = os.environ["DB_CERT"]
        db_key = os.environ["DB_KEY"]

        ssl_args = {"ssl_ca": db_root_cert, "ssl_cert": db_cert, "ssl_key": db_key}
        connect_args = ssl_args

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = connect_args
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
