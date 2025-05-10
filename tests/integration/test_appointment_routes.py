from datetime import datetime
from flask.testing import FlaskClient

def test_appt_all(app, client: FlaskClient, pt_reg_form1, dr_reg_form1):
    client, db = client
    res1 = client.post('/register/', json=pt_reg_form1)
    res2 = client.post('/register/', json=dr_reg_form1)
    assert res1.is_json 
    assert res2.is_json 
    id1 = res1.json.get('user_id')
    id2 = res2.json.get('user_id')
    assert isinstance(id1, int)
    assert isinstance(id2, int)
    res3 = client.post('/auth/login', json={
        "username": pt_reg_form1["username"],
        "password": pt_reg_form1["password"],
    })
    res4 = client.post('/auth/login', json={
        "username": dr_reg_form1["username"],
        "password": dr_reg_form1["password"],
    })
    assert res3.is_json
    assert res4.is_json
    tok1 = res3.json.get('token')
    tok2 = res4.json.get('token')
    assert tok1 != tok2

    res5 = client.post(
        f'/request/patient/{id1}/doctor/{id2}', 
        headers=[('Authorization', f'Bearer {tok1}')]
    )

    assert (
        (res7 := client.get(f'/user/{id1}', headers=[('Authorization', f'Bearer {tok1}')]))
            .json.get('doctor')
            .get('doctor_id') == id2
    )
    assert res7.status_code == 200
    with app.test_request_context(
        '/appointment/add', method='POST', 
        headers={'Authorization': f'Bearer {tok1}'},
        json={
            "doctor_id": id2,
            "patient_id": id1,
            "treatment": "consult",
            "start_date": datetime.now()
        },
    ) as ctx:
        from flaskr.routes.appointment_routes import create_appointment
        from flaskr.services.appointment_service import add_appointment
        r8 = create_appointment()
        assert r8[1] == 400
        r9 = add_appointment(
            ctx.request.json.get('doctor_id'), 
            ctx.request.json.get('patient_id'),
            ctx.request.json.get('treatment'),
            datetime.now()
        )
        assert r9 == 1

    r10 = client.get(f'/appointment/upcoming/{id1}', headers={'Authorization': f'Bearer {tok1}'})
    r11 = client.get(f'/appointment/upcoming/{id2}', headers={'Authorization': f'Bearer {tok2}'})
    assert r10.is_json
    assert r11.is_json
    assert r10.status_code == 200
    assert r11.status_code == 200
    assert r10.json[0] == r11.json[0]

    r12 = client.get(f'/appointment/{r9}', headers={'Authorization': f'Bearer {tok1}'})
    assert r12.is_json
    assert r12.status_code == 200

    r13 = client.put(f'/appointment/update/{r9}', headers={'Authorization': f'Bearer {tok2}'}, json={
        'status': 'CANCELLED',
        'treatment': 'consult',
        'start_date': datetime.now()
    })
    assert r13.status_code == 400

    with app.test_request_context(
        f'/appointment/update/{r9}', method='PUT', 
        headers={'Authorization': f'Bearer {tok2}'},
        json={
            "treatment": "consult",
            "start_date": datetime.now(),
            "status": "CANCELLED"
        },
    ) as ctx:
        from flaskr.routes.appointment_routes import update_appointment_detail
        from flaskr.services.appointment_service import update_appointment
        from flaskr.models import User
        r14 = update_appointment_detail(r9)
        assert 'error' in r14[0].json
        r15 = update_appointment(
            r9,
            ctx.request.json.get('treatment'),
            datetime.now(),
            ctx.request.json.get('status'),
            None,
            User.query.filter_by(user_id=id2).first()
        )
        assert r15 is None
    r16 = client.get(f'/appointment/{r9}', headers={'Authorization': f'Bearer {tok1}'})
    assert r16.json.get('status') == 'CANCELLED'