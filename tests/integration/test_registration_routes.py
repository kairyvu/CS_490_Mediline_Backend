import copy
from flask import Request, Response
from flask.testing import FlaskClient

####======TESTS=====####
def test_register_add_user(client: FlaskClient, pt_reg_form1):
    client, db = client
    response = client.post(
        '/register/',
        follow_redirects=True,
        json=pt_reg_form1
    )
    assert response.json.get('user_id')

def test_register_add_duplicate_user(client: FlaskClient, pt_reg_form1):
    client, db = client
    response = client.post('/register/', json=pt_reg_form1)
    assert response.json.get('user_id')
    response = client.post('/register/', json=pt_reg_form1)
    assert response.status_code == 400

def test_register_incomplete(client: FlaskClient, pt_reg_form1):
    client, db = client
    USER1_CPY = copy.deepcopy(pt_reg_form1)
    USER1_CPY.pop('email')

    res: Response = client.post('/register/', json=USER1_CPY)
    assert res.status_code == 400
    assert b"&#39;email&#39; is a required property" in res.data

def test_register_no_data(client: FlaskClient):
    client, db = client
    res: Response = client.post('/register/')
    assert res.status_code == 415
    assert b"<h1>Unsupported Media Type</h1>" in res.data

def test_register_no_data_2(client: FlaskClient):
    client, db = client
    res: Response = client.post('/register/', json={})
    print(res)
    assert res.status_code == 400
    assert b"is a required property" in res.data

def test_register_bad_acct_type(client: FlaskClient, pt_reg_form1):
    client, db = client
    USER1_CPY = copy.deepcopy(pt_reg_form1)
    USER1_CPY['account_type'] = 'pt'
    res: Response = client.post('/register/', json=USER1_CPY)

    print(res.data)
    assert res.status_code == 400