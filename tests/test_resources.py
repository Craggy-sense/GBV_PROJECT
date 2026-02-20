from app.chatbot.resources import get_all_resources, format_resources_to_text

def test_get_all_resources():
    resources = get_all_resources()
    assert len(resources) > 0
    assert "name" in resources[0]
    assert "contact" in resources[0]

def test_format_resources_to_text():
    formatted_text = format_resources_to_text()
    assert "Gender Violence Recovery Centre" in formatted_text
    assert "1195" in formatted_text
    assert "Important Support Resources in Kenya" in formatted_text
