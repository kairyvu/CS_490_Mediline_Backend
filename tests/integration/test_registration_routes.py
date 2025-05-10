import copy
from flask import Request, Response
from flask.testing import FlaskClient

####======TESTS=====####
# def test_register_add_user(client: FlaskClient, pt_reg_form1):
#     client, db = client
#     response = client.post(
#         '/register/',
#         follow_redirects=True,
#         json=pt_reg_form1
#     )
#     assert response.json.get('user_id')

# def test_register_add_duplicate_user(client: FlaskClient, pt_reg_form1):
#     client, db = client
#     response = client.post('/register/', json=pt_reg_form1)
#     assert response.json.get('user_id')
#     response = client.post('/register/', json=pt_reg_form1)
#     assert response.status_code == 400

def test_register_incomplete(client: FlaskClient, pt_reg_form1):
    client, db = client
    USER1_CPY = copy.deepcopy(pt_reg_form1)
    USER1_CPY.pop('email')

    res: Response = client.post('/register/', json=USER1_CPY)
    assert res.status_code == 400
    assert res.is_json
    res_json = res.json
    assert 'error' in res_json
    assert isinstance(res_json['details'], list)
    assert isinstance(res_json['details'][0], dict)
    assert 'email' in res_json['details'][0]
    assert res_json['details'][0]['email'] == 'This field is required.'

def test_register_no_data(client: FlaskClient):
    client, db = client
    res: Response = client.post('/register/')
    assert res.is_json
    assert res.status_code == 415
    
def test_register_no_data_2(client: FlaskClient):
    client, db = client
    res: Response = client.post(
        '/register/', 
        headers={ 'Content-type':'application/json', }
    )
    assert res.is_json
    assert res.status_code == 400

def test_register_no_data_3(client: FlaskClient):
    client, db = client
    res: Response = client.post('/register/', json={})
    assert res.status_code == 400

def test_register_bad_acct_type(client: FlaskClient, pt_reg_form1):
    client, db = client
    USER1_CPY = copy.deepcopy(pt_reg_form1)
    USER1_CPY['account_type'] = 'pt'
    res: Response = client.post('/register/', json=USER1_CPY)

    assert res.status_code == 400
    assert res.json['error'] == "'pt' is not one of ['patient', 'doctor', 'pharmacy']"

def test_get_register(client: FlaskClient):
    client, _ = client
    res = client.get('/register/')
    assert res.status_code == 405
    assert res.json['error'] == 'The method is not allowed for the requested URL.'