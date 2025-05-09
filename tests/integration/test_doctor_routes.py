import pytest
from datetime import datetime
from flask.testing import FlaskClient

def test_dr_all(app, client: FlaskClient, dr_reg_form1):
    from flaskr.services import add_user
    from werkzeug.datastructures import ImmutableMultiDict
    client, _ = client
    assert client.get('/doctor', follow_redirects=True).json == []
    assert (client.get('/doctor', follow_redirects=True).json
            == client.get('/doctor/').json)
    d1 = add_user(ImmutableMultiDict(list(dr_reg_form1.items()))).json.get('user_id')
    tok = client.post('/auth/login', json={
        "username": dr_reg_form1['username'],
        "password": dr_reg_form1['password'],
    }).json.get('token')

    assert len(client.get('/doctor/').json) != 0
    assert client.get(
        f'/doctor/{d1}/appointment_requests',
        headers={'Authorization': f'Bearer {tok}'}
    ).json == []
    assert (r1 := client.get(
        f'/doctor/{d1}/doctor-patients',
        headers={'Authorization': f'Bearer {tok}'}
    ).json).get('patients') == []
    assert r1.get('doctor_patients_count') == 0
    assert client.get(
        f'/doctor/{d1}/discussions',
        headers={'Authorization': f'Bearer {tok}'}
    ).json == []
    assert client.get(
        f'/doctor/{d1}/patients-today',
        headers={'Authorization': f'Bearer {tok}'}
    ).json == []
    assert client.get(
        f'/doctor/{d1}/pending-appointments/count',
        headers={'Authorization': f'Bearer {tok}'}
    ).json.get('pending_appointments_count') == 0
    assert client.get(
        f'/doctor/{d1}/upcoming-appointments/count',
        headers={'Authorization': f'Bearer {tok}'}
    ).json.get('upcoming_appointments_count') == 0
    assert (r2 := client.get(
        f'/doctor/{d1}/ratings',
        headers={'Authorization': f'Bearer {tok}'}
    ).json).get('ratings') == []
    assert r2.get('average_rating') == 0
    with app.test_request_context(
        f'/doctor/{d1}', method='PUT',
        headers={'Authorization': f'Bearer {tok}'},
        json={
            'accepting_patients': False
        }
    ) as ctx:
        from flaskr.routes.doctor_routes import update_doctor_info
        from flaskr.services import update_doctor
        assert update_doctor_info(d1)[1] == 500
        with pytest.raises(Exception):
            update_doctor(d1, {'accepting_patients': False})
