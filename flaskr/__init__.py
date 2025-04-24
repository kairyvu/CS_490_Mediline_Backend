from flask import Flask
import os
from dotenv import load_dotenv
from flask_cors import CORS

    
load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r"/*": {"origins": "*"}})

    database = os.getenv("DB_NAME", "doctor_patient_system")
    connection_string = 'mysql+pymysql://'
    if os.environ.get('FLASK_ENV') == 'development':
        # When running app on local machine
        username = os.getenv("DB_USER") or os.getenv("MYSQL_USER", "root")
        password = os.getenv("DB_PASS") or os.getenv("MYSQL_PASSWORD", "")
        host = os.getenv("INSTANCE_HOST") or os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        connection_string += f'{username}:{password}@{host}:{port}/{database}'
        app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    else:
        # Production on gcloud
        from flaskr.extensions import connector
        from pymysql.connections import Connection
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

                                            
    app.config['SWAGGER'] = { 'doc_dir': './docs/' }

    from flaskr.extensions import db
    db.init_app(app)

    from flask_migrate import Migrate
    migrate = Migrate(app, db)

    from flaskr.extensions import swag
    swag.init_app(app)
    
    from flaskr.routes import register_routes
    register_routes(app)
    from flaskr.cli import register_commands
    register_commands(app)

    return app
