import os
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

class CloudSqlConnector:
    def __init__(self):
        self._connector = None

    def connect(self, instance_connection_name, driver, **kwargs):
        if self._connector is None:
            from google.cloud.sql.connector import Connector
            ip_type = os.getenv("DB_IP_TYPE", "PUBLIC_IP")
            self._connector = Connector(
                ip_type=ip_type,
                refresh_strategy="LAZY"
            )
        return self._connector.connect(instance_connection_name, driver, **kwargs)

db = SQLAlchemy()
swag = Swagger(
    template_file=os.path.join(
        os.getcwd(), 'flaskr', 'docs', 'template.yml'
    ),
    parse=True
)