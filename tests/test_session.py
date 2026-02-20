import time
from app.chatbot.session import get_session_history, append_to_history, clear_session, sessions, SESSION_TIMEOUT_SECONDS

def test_new_session_creation():
    phone = "12345"
    clear_session(phone)
    history = get_session_history(phone)
    assert len(history) == 0
    assert phone in sessions

def test_append_to_history():
    phone = "67890"
    clear_session(phone)
    append_to_history(phone, "user", "Hello")
    history = get_session_history(phone)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"

def test_session_history_limit():
    phone = "limit_test"
    clear_session(phone)
    for i in range(15):
        append_to_history(phone, "user", f"msg {i}")
    
    history = get_session_history(phone)
    assert len(history) == 10  # Should be capped at 10
    assert history[-1]["content"] == "msg 14"

def test_session_timeout():
    phone = "timeout_test"
    clear_session(phone)
    append_to_history(phone, "user", "Old msg")
    
    # Manually backdate the session
    sessions[phone]["last_interaction"] = time.time() - (SESSION_TIMEOUT_SECONDS + 10)
    
    # Next call should clear history because of timeout
    history = get_session_history(phone)
    assert len(history) == 0
