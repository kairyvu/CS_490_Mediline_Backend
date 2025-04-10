import os
from dotenv import load_dotenv

from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flaskr.cli import register_commands

load_dotenv()

def create_app(test_db_uri: str|None=None):
    app = Flask(__name__, instance_relative_config=True)

    # From .env load mysql authentication
    username = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("MYSQL_HOST", "localhost")
    schema = os.getenv("MYSQL_DATABASE")
    app.config['SQLALCHEMY_DATABASE_URI'] = test_db_uri or f'mysql+pymysql://{username}:{password}@{host}/{schema}'

    from flaskr.extensions import db
    db.init_app(app)
    migrate = Migrate(app, db)
    
    from flaskr.routes import register_routes
    register_routes(app)
    register_commands(app)

    return app