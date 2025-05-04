import os
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

_connector = None
def get_connector():
    global _connector
    if _connector is None:
        from google.cloud.sql.connector import Connector, IPTypes

        ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
        _connector = Connector(ip_type=ip_type, refresh_strategy="LAZY")
    return _connector

def getconn():
    connector = get_connector()
    instance_conn_name = os.getenv("INSTANCE_CONNECTION_NAME")
    db_name            = os.getenv("DB_NAME")

    def creator():
        return connector.connect(
            instance_conn_name,
            "pymysql",
            user=os.getenv("DB_IAM_USER"),
            enable_iam_auth=True,
            db=db_name,
        )

    return creator

db = SQLAlchemy()
swag = Swagger(
    template_file=os.path.join(
        os.getcwd(), 'flaskr', 'docs', 'template.yml'
    ),
    parse=True
)