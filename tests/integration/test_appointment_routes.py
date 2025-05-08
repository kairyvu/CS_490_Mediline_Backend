from datetime import datetime
from flask import Request, Response
from flask.testing import FlaskClient

import flaskr.models

####======TESTS=====####
def test_create_appt(monkeypatch, client: FlaskClient, pt_reg_form1, dr_reg_form1):
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
    assert res5.status_code == 201
    assert isinstance((req_id := res5.json['request_id']), int)
    res6 = client.delete(
        f'/request/{req_id}',
        json={"status": "accepted"},
        headers=[('Authorization', f'Bearer {tok2}')]
    )

    assert res6.status_code == 200
    assert (
        (res7 := client.get(f'/user/{id1}', headers=[('Authorization', f'Bearer {tok1}')]))
            .json.get('doctor')
            .get('doctor_id') == id2
    )
    assert res7.status_code == 200
    import flaskr.models
    from flaskr.models import AppointmentDetail
    from flaskr.struct import AppointmentStatus
    class MockApptDetail(AppointmentDetail):
        def __init__(self, treatment='', start_date: str|datetime=datetime.now(), 
                     end_date=None, status=AppointmentStatus.PENDING):
            print("FUCK!!!!")
            super(
                treatment=treatment,
                start_date=datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date,
                end_date=end_date,
                status=status
            )
                
    def add_apptfix(d_id, p_id, treat, start, end=None):
        from flaskr.models import AppointmentDetail, Appointment
        start = datetime.fromisoformat(start)
        appointment_detail = AppointmentDetail(
            treatment=treat,
            start_date=start,
            end_date=end,
            status=AppointmentStatus.PENDING
        )
        appointment = Appointment(
            doctor_id=d_id,
            patient_id=p_id,
            appointment_detail=appointment_detail
        )
        db.session.add(appointment)
        db.session.flush()
        appointment_detail.appointment_details_id = appointment.appointment_id
        db.session.commit()
        return appointment.appointment_id
    monkeypatch.setattr('flaskr.routes.appointment_routes.create_appointment', lambda: print('JESUS FUCKING CHRIST'))
    res8 = client.post(
        '/appointment/add',
        json={
            'doctor_id': id2,
            'patient_id': id1,
            'start_date': datetime.now().isoformat(),
            'treatment': 'consult'
        },
        headers=[('Authorization', f'Bearer {tok1}')]
    )
    print(res8.json)
    assert res8.status_code == 201
    assert res8.is_json
    assert isinstance(res8.json['id'], int)

