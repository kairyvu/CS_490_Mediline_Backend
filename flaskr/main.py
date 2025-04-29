
"""
from flaskr import create_app
from socketio import Server, WSGIApp
import gunicorn
flask_app = create_app()
celery_app = flask_app.extensions['celery']
celery_app.autodiscover_tasks(['flaskr', 'flaskr.celery_utils'])
sio = Server(
    namespaces='*',
    cors_allowed_origins='*', 
    always_connect=True, 
    ping_timeout=60
)
socketio_app = WSGIApp(sio, flask_app)
"""

from flaskr import create_app
from flaskr.extensions import sio
flask_app = create_app()
celery = flask_app.extensions['celery']
if __name__ == '__main__':
    app = sio.run(flask_app)