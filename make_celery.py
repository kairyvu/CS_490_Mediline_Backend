# Module needed to instantiate celery app
from flaskr import create_app

flask_app = create_app()
celery_app = flask_app.extensions['celery']