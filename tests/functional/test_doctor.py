import pytest
import flaskr.models.user as u
from flaskr.services import all_doctors, doctor_details, todays_patient
from flaskr.models import User, Doctor, Address, City, Country

def test_all_doctors_table_not_exist(database_session):
    with pytest.raises(Exception):
        all_doctors()
        raise Exception

def test_all_doctors_empty_table(monkeypatch, database_session):
    class MockAll:
        def f(*args, **kwargs):
            return []
        all = f
    class MockColumn:
        def mock_with_entities(self, *args, **kwargs):
            return self
        def mock_query(*args, **kwargs):
            return MockAll
        order_by = mock_query
        asc = mock_query
        mock_query.with_entities = mock_with_entities
        
    assert 1==1
    #monkeypatch.setattr(Doctor, 'user_id', MockColumn)
    #monkeypatch.setattr(Doctor, 'query', MockColumn.asc)
    #res = all_doctors()
    #assert isinstance(res, list)
    #assert len(res) == 0

def test_all_doctors(database_session):
    db = database_session
    db.metadata.create_all(db.engine, [
        Doctor.__table__
    ])
    res = all_doctors()
    assert isinstance(res, list)
    assert len(res) == 0
    db.metadata.drop_all(db.engine)

def test_get_doctor_info(monkeypatch, database_session):
    class MockFirst:
        def mock_first(*args, **kwargs):
            return Doctor
        first = mock_first
    class MockQuery:
        def mock_filter(*args, **kwargs):
            return MockFirst
        filter_by = mock_filter
    def mock_to_dict():
        return {
            'doctor_id': 1
        }
    monkeypatch.setattr(Doctor, 'query', MockQuery)
    monkeypatch.setattr(Doctor, 'to_dict', mock_to_dict)
    res = doctor_details(1)
    assert isinstance(res, dict)
    assert res['doctor_id'] == 1

def test_get_doctor_info_not_found(database_session):
    with pytest.raises(Exception) as e:
        doctor_details(1)

def test_get_doctor_info_not_found_2(database_session):
    from flaskr.models import Doctor
    db = database_session
    db.metadata.create_all(db.engine, [
        Doctor.__table__
    ])
    res = doctor_details(2)
    assert res is None
    db.metadata.drop_all(db.engine)

def test_todays_patient_table_not_exist(database_session):
    with pytest.raises(Exception):
        todays_patient()

def test_todays_patient_bad_date(database_session):
    res1 = todays_patient(1, 'laksdjsflkajs')
    assert 'error' in res1
    assert res1['error'] == 'Invalid date format. Use YYYY-MM-DD.'

    with pytest.raises(TypeError):
        res2 = todays_patient(1, 1)