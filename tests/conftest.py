import pytest

from flaskr import create_app
from flaskr.extensions import db
from flaskr.models import User, Doctor, Patient, Pharmacy

# --------
# Fixtures
# --------
@pytest.fixture(scope='module')
def test_client():
    # Set up testing config
    flask_app = create_app()
    flask_app.testing = True

    # Create a test client
    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            yield test_client

@pytest.fixture(scope='module')
def new_user():
    user = User(
        username='test',
        password='test',
        account_type='test',
    )
    return user

"""
@pytest.fixture(scope='module')
def init_database(test_client):
    db.create_all()
"""




"""
@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
    })

    yield app

@pytest.fixture()
def client(app):
    return app
"""