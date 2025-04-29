"""
from flaskr import create_app

flask_app = create_app()
celery = flask_app.extensions['celery']
celery.autodiscover_tasks(['flaskr', 'flaskr.celery_utils'])
"""