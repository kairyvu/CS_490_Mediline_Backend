from datetime import datetime
import pytest
import flaskr.services
from flaskr.services import get_current_chat
from flaskr.models import User, Patient, Doctor, Appointment, Chat, Message
from flaskr.struct import AccountType

def test_get_current_chat_not_found(database_session): 
    db = database_session
    db.metadata.create_all(db.engine, [
        Chat.__table__,
    ])
    with pytest.raises(ValueError):
        get_current_chat(1)
    db.metadata.drop_all(db.engine)

def test_get_current_chat(monkeypatch, database_session): 
    class MockChat:
        @staticmethod
        def first():
            return Chat
    class MessageList:
        m = [
            {
                'message_id': 1,
                'chat_id': 1,
                'user_id': 1,
                'message_content': 'Hello',
                'time': datetime.time(datetime.now()).isoformat()
            }
        ]

    def mock_to_dict():
        return {
            'chat_id': Chat.chat_id,
            'appointment_id': Chat.appointment_id,
            'start_date': datetime.now().isoformat(),
            'messages': Chat.messages.m

        }
    def mock_query():
        pass
    def mock_filter(appointment_id):
        return MockChat
    mock_query.filter_by = mock_filter
    monkeypatch.setattr(Appointment, 'appointment_id', 1)
    monkeypatch.setattr(Appointment, 'doctor_id', 1)
    monkeypatch.setattr(Appointment, 'patient_id', 2)
    monkeypatch.setattr(Chat, 'chat_id', 1)
    monkeypatch.setattr(Chat, 'appointment_id', 1)
    monkeypatch.setattr(Chat, 'appointment', Appointment)
    monkeypatch.setattr(Chat, 'messages', MessageList)
    monkeypatch.setattr(User, 'account_type', AccountType.SUPERUSER)
    monkeypatch.setattr(Chat, 'query', mock_query)
    monkeypatch.setattr(Chat, 'to_dict', mock_to_dict)

    assert Appointment.appointment_id == 1
    assert Appointment.doctor_id == 1
    assert Appointment.patient_id == 2
    res = get_current_chat(1, User)
    assert isinstance(res, dict)