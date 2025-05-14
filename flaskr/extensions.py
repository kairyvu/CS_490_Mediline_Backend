import os

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flasgger import Swagger

from google.cloud.sql.connector import Connector, IPTypes

ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
connector = Connector(ip_type=ip_type, refresh_strategy="LAZY")
db = SQLAlchemy()
swag = Swagger(
    template_file=os.path.join(
        os.getcwd(), 'flaskr', 'docs', 'template.yml'
    ),
    parse=True
)

jwt = JWTManager()

## SocketIO stuff
sio = SocketIO(
    ping_timeout=60,
    cors_allowed_origins='*',
    always_connect=True, 
    namespaces='*',
    logger=True,
    engineio_logger=True
)