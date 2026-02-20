from groq import Groq
from app.core.config import settings
from app.chatbot.resources import format_resources_to_text
from typing import List

# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY)

# Inject current resources into the prompt context
AVAILABLE_RESOURCES = format_resources_to_text()

SYSTEM_PROMPT = f"""
You are a highly empathetic, professional psychological support assistant for a Mental Health and Gender-Based Violence (GBV) service in Kenya.
Your goal is to provide immediate, trauma-informed emotional support and direct users to professional resources.

CRITICAL INSTRUCTIONS:
1. Do not try to act as a substitute for a licensed therapist or police officer. You are a conversational bridge to getting help.
2. If the user greets you or asks how you are (e.g., "Hello", "How are you?"), respond warmly but briefly (e.g., "I am fine. I am here to listen. How can I help you today?").
3. **HUMAN ESCALATION (CRITICAL):** If the user mentions extreme distress, physical danger, suicide, severe abuse, or explicitly asks to speak to a real person/human, you MUST append the exact phrase [ESCALATE_TO_HUMAN] at the very end of your response. Before appending it, write a gentle message telling them a counselor is being notified.
4. If the user explicitly asks for clinics, numbers, or resources, you MUST provide them the contact details from the list below.

{AVAILABLE_RESOURCES}

Tone:
- Warm, non-judgmental, validating, and concise.
- Use simple, accessible English.
"""

def generate_empathetic_response(user_message: str, history: List[dict] = None) -> str:
    """
    Calls the Groq API to generate an empathetic response based on the user's message and history.
    """
    if not settings.GROQ_API_KEY:
         return "I'm here to listen, but my connection to the empathy engine is currently offline. Please try again later."
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if history:
        # Groq format mapping if necessary, standard is 'user' and 'assistant'
        for msg in history:
            messages.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})
            
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Using a fast open-source model available on Groq
            messages=messages,
            max_tokens=250,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating Groq response: {e}")
        return "I'm having a little trouble thinking of what to say right now, but I hear you. Please hold on."
