import os
from dotenv import load_dotenv
import pytest
import sqlalchemy as sa

import subprocess

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from flaskr.models import User, Doctor, Patient, Pharmacy

load_dotenv()

pytest_plugins = ['pytest-flask-sqlalchemy']

# --------
# Fixtures
# --------
@pytest.fixture(scope='module')
def new_user():
    user = User(
        username='test',
        password='test',
        account_type='test',
    )
    return user

"""
This plugin assumes that a fixture called _db has been defined in the root conftest file for your tests. 
The _db fixture should expose access to a valid SQLAlchemy Session object 
that can interact with your database, for example via the SQLAlchemy initialization 
class that configures Flask-SQLAlchemy.

The fixtures in this plugin depend on this _db fixture to access your database 
and create nested transactions to run tests in. 
You must define this fixture in your conftest.py file for the plugin to work.
"""
# Retrieve a database connection string from the shell environment
try:
    DB_CONN = os.getenv('TEST_DATABASE_URL')
except KeyError:
    raise KeyError('TEST_DATABASE_URL not found. You must export a database ' +
                   'connection string to the environmental variable ' +
                   'TEST_DATABASE_URL in order to run tests.')
else:
    DB_OPTS = sa.engine.url.make_url(DB_CONN).translate_connect_args()

pytest_plugins = ['pytest-flask-sqlalchemy']
engine = sa.create_engine(DB_CONN)
conn = engine.raw_connection()
#engine = db.get_engine().raw_connection()

@pytest.fixture(scope='session')
def database(request):
    '''
    Create a mysql database for the tests, and drop it when the tests are done.
    '''
    """
    mysql_host = DB_OPTS.get("host")
    mysql_port = DB_OPTS.get("port")
    mysql_user = DB_OPTS.get("username")
    mysql_pw = DB_OPTS.get("password")
    """
    mysql_db = DB_OPTS["database"]

    # Create the database in mysql given the connection url
    '''
    cnx = db.session.connection()
    cur = cnx.connection.cursor()
    cur.execute(f'CREATE SCHEMA {mysql_db}')
    '''
    cur = conn.cursor()
    #cur.executemany()
    cur.execute(f'DROP SCHEMA IF EXISTS {mysql_db}')
    cur.execute(f'CREATE SCHEMA {mysql_db}')

    @request.addfinalizer
    def drop_database():
        cur = conn.cursor()
        cur.execute(f'DROP SCHEMA IF EXISTS {mysql_db}')

@pytest.fixture(scope='session')
def test_client(database):
    DB_MIGRATIONS = '\
        python -m flask db init -d test_migrations ; \
        python -m flask db migrate -d test_migrations ; \
        python -m flask db upgrade'
    subprocess.run(
        DB_MIGRATIONS,
        shell=True,
        executable='/bin/bash'
    )
    # Set up testing config
    flask_app = create_app(DB_CONN)
    flask_app.testing = True
    flask_app.config.update({
        "TESTING": True
    })

    DB_SEED = 'flask seed-db'
    subprocess.run(
        DB_SEED,
        shell=True,
        executable='/bin/bash'
    )

    # Create a test client
    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            yield test_client

@pytest.fixture(scope='session')
def _db(test_client):
    from flaskr.extensions import db
    return db


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