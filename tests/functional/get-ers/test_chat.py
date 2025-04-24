import pytest
from flaskr.services.chat_service import get_current_chat

def test_get_current_chat_not_found(database_session): 
    from flaskr.models import Chat
    db = database_session
    db.metadata.create_all(db.engine, [
        Chat.__table__,
    ])
    with pytest.raises(ValueError):
        get_current_chat(1)
    db.metadata.drop_all(db.engine)

def test_get_current_chat(database_session, chat1): 
    from flaskr.models import User, Patient, Doctor, Appointment, Chat, Message
    db = database_session
    db.metadata.create_all(db.engine, [
        User.__table__,
        Patient.__table__,
        Doctor.__table__,
        Appointment.__table__,
        Chat.__table__,
        Message.__table__
    ])
    chat, appt = chat1
    db.session.add_all([chat, appt])
    db.session.flush()
    res = get_current_chat(1)
    assert isinstance(res, dict)
    assert {
        'chat_id',
        'appointment_id',
        'start_date',
        'messages'
    } <= set(res)
    assert len(res['messages']) == 2
    assert {
        'message_id',
        'chat_id',
        'user_id',
        'message_content',
        'time'
    } <= set(res['messages'][0])
    db.session.rollback()
    db.metadata.drop_all(db.engine)
