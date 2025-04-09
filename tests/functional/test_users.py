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

def test_register_post(test_client: FlaskClient):
    """
    GIVEN a Flask app
    WHEN the '/register/' page is requested
    THEN check '405' is returned
    """
    #data = 
    response = test_client.get('/register/')
    assert response.status_code == 405
