import os
from werkzeug.exceptions import abort
from flask import Flask, make_response, jsonify

from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

from celery import Celery, Task
from google.cloud.sql.connector import Connector, IPTypes

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
connector = Connector(ip_type=ip_type, refresh_strategy="LAZY")
db = SQLAlchemy()
swag = Swagger(
    template_file=os.path.join(
        os.getcwd(), 'flaskr', 'docs', 'template.yml'
    ),
    parse=True
)