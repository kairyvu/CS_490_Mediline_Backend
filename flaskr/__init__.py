import os

from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from flaskr.extensions import db, swag, jwt, sio
from flaskr.models import User
from flaskr.routes import register_routes
from flaskr.cli import register_commands

from dotenv import load_dotenv
    
load_dotenv()

def create_app(config_mapping: dict|None=None):
    app = Flask(__name__, instance_relative_config=True)
    
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Ensures all error responses are returned as JSON
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        return jsonify(error=str(e.description)), e.code
    
    database = os.getenv("DB_NAME", "doctor_patient_system")
    connection_string = 'mysql+pymysql://'
    if config_mapping and config_mapping.get("TESTING"):
        app.config.from_mapping(config_mapping)
    elif os.environ.get('FLASK_ENV') == 'development':
        # When running app on local machine
        print("***IN DEVELOPMENT MODE***")
        app.config['FLASK_ENV'] = 'development'
        username = os.getenv("DB_USER") or os.getenv("MYSQL_USER", "root")
        password = os.getenv("DB_PASS") or os.getenv("MYSQL_PASSWORD", "")
        host = os.getenv("INSTANCE_HOST") or os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        connection_string += f'{username}:{password}@{host}:{port}/{database}'
        app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    elif os.getenv('FLASK_ENV') in ['prod', 'production']:
        # Production on gcloud
        from flaskr.extensions import connector
        from pymysql.connections import Connection
        app.config['FLASK_ENV'] = 'prod'
        instance_conn_name = os.getenv("INSTANCE_CONNECTION_NAME")
        def getconn() -> Connection:
            conn: Connection = connector.connect(
                instance_conn_name,
                'pymysql',
                user=os.getenv("DB_IAM_USER"),
                enable_iam_auth=True,
                db=database
            )
            return conn
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = { "creator": getconn }
        app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
                                            
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')
    app.config['SWAGGER'] = { 'doc_dir': './docs/' }

    db.init_app(app)
    migrate = Migrate(app, db)
    swag.init_app(app)
    jwt.init_app(app)
    ### TODO: Move these registrations somewhere else for code cleanliness maybe
    ## Register jwt related callbacks here to prevent circular import
    # Callback that returns user_id
    @jwt.user_identity_loader
    def user_id_cb(user):
        return str(user.user_id)

    # Callback to load user from db on protected route access
    @jwt.user_lookup_loader
    def user_lookup_cb(_jwt_header, jwt_data):
        identity = int(jwt_data['sub'])
        return User.query.filter_by(user_id=identity).one_or_none()
    
    register_routes(app)
    register_commands(app)

    sio.init_app(app)

    return app