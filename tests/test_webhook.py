from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_webhook_receives_message():
    response = client.post(
        "/api/v1/whatsapp/webhook",
        data={"From": "whatsapp:+123456789", "Body": "Hello, I need help"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    
    response_xml = response.text
    # Basic structural check
    assert "<Response><Message>" in response_xml
    assert "</Message></Response>" in response_xml
    
def test_webhook_clear_session():
    response = client.post(
        "/api/v1/whatsapp/webhook",
        data={"From": "whatsapp:+123456789", "Body": "/clear"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "Session cleared" in response.text
