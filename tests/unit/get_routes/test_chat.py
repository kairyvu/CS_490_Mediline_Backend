import pytest
from flaskr.services.chat_service import get_current_chat

def test_get_current_chat(database_session): 
    with pytest.raises(ValueError):
        get_current_chat(1)
