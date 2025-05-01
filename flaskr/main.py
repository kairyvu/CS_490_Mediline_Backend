from flaskr import create_app
from flaskr.extensions import sio
flask_app = create_app()
celery = flask_app.extensions['celery']
if __name__ == '__main__':
    app = sio.run(flask_app)