def test_chat(chat1):
    from flaskr.models import Appointment
    chat, _ = chat1
    assert chat.chat_id == 1
    assert chat.appointment_id == 1
    assert isinstance(chat.appointment, Appointment)

def test_chat_messages(chat1):
    chat, _ = chat1
    assert isinstance(chat.messages, list)
    assert chat.messages[0].time < chat.messages[1].time
