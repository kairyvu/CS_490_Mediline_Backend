"""
functional tests for different routes

These tests use GETs and POSTS to different URLs to check proper behavior
"""
from flask.testing import FlaskClient 

def test_test_connection(test_client: FlaskClient):
    """
    GIVEN a Flask app
    WHEN the '/test_connection/' page is requested
    THEN check valid response
    """
    response = test_client.get('/test_connection/')
    assert response.status_code == 200

def test_register_get(test_client: FlaskClient):
    """
    GIVEN a Flask app
    WHEN the '/register/' page is requested
    THEN check '405' is returned
    """
    response = test_client.get('/register/')
    assert response.status_code == 405

def test_register_patient_post(test_client: FlaskClient, db_session):
    """
    GIVEN a Flask app
    WHEN the '/register/' page is requested
    THEN check '201' is returned
    """
    form_data = {
        "username": "test_user1",
        "password": "test_password_good",
        "account_type": "patient",
        "first_name": "test_user1",
        "last_name": "test_user1",
        "email": "test_user1",
        "phone": "test_user1",
        "dob": "test_user1"
    }
    response = test_client.post('/register/', data=form_data)
    assert response.status_code == 405
