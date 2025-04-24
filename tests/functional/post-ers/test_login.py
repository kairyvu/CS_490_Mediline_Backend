import pytest
from flaskr.services import user_id_credentials

def test_table_not_exist():
    with pytest.raises(Exception):
        user_id_credentials('','')

def test_user_not_exist(database_session):
    from flaskr.models import User
    db = database_session
    db.metadata.create_all(db.engine, [
        User.__table__
    ])
    assert user_id_credentials('', '') is None
    db.metadata.drop_all(db.engine)

def test_user_authenticate(database_session, pt1):
    from flaskr.models import User, Patient
    db = database_session
    db.metadata.create_all(db.engine, [
        User.__table__,
        Patient.__table__
    ])
    user, user_pt = pt1
    db.session.add_all([user, user_pt])
    db.session.flush()
    res = user_id_credentials('user1', 'password1')
    assert isinstance(res, dict)
    assert {'user_id', 'account_type'} <= set(res)
    assert res['user_id'] == 1
    assert res['account_type'] == 'patient'
    db.session.rollback()
    db.metadata.drop_all(db.engine)
