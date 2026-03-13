from fastapi import APIRouter, Request, BackgroundTasks, Depends
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.chatbot.nlp import generate_empathetic_response
from app.chatbot.session import get_session_history, append_to_history, clear_session, is_human_handoff_active, trigger_human_handoff
from app.db import crud

router = APIRouter()

@router.post("/webhook")
async def twilio_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Receives incoming WhatsApp messages from Twilio.
    """
    form_data = await request.form()
    incoming_msg = form_data.get('Body', '').strip()
    sender_number = form_data.get('From', '')

    # Log receipt of message here (ensure PII is handled securely)
    print(f"Received message from {sender_number}: {incoming_msg}")
    
    # Handle clearing session
    if incoming_msg.lower() == "/clear":
         clear_session(db, sender_number)
         resp = MessagingResponse()
         resp.message("Session cleared. Let me know if you need anything else.")
         return Response(content=str(resp), media_type="application/xml")

    # Step 0: Check if Human Handoff is already active
    user = crud.get_or_create_user(db, sender_number)
    if user.is_escalated:
         # Log the user's message to the history but DO NOT call the AI
         append_to_history(db, sender_number, "user", incoming_msg)
         
         # Only send the automated message if NO ONE has claimed it yet
         # This prevents annoying the user with repetitive messages once they are talking to a human
         if not user.claimed_by_mentor_id:
             resp = MessagingResponse()
             resp.message("A counselor is still reviewing your messages. We will reply shortly. Please hold on.")
             return Response(content=str(resp), media_type="application/xml")
         
         # If claimed, we stay silent and let the mentor handle the conversation
         resp = MessagingResponse()
         return Response(content=str(resp), media_type="application/xml")

    # Step 1: Detect and Translate incoming message to English (Option 2)
    from app.chatbot.translation import detect_and_translate_to_english, translate_from_english
    english_msg, detected_lang = detect_and_translate_to_english(incoming_msg)
    print(f"Detected Language: {detected_lang}, Translated to English: {english_msg}")

    # Step 2: Get conversation history for this sender
    history = get_session_history(db, sender_number)

    # Step 3: Generate empathetic response securely in English
    bot_response_english = generate_empathetic_response(english_msg, history)

    # Step 3.5: Check for Human Handoff Trigger
    needs_human = False
    if "[ESCALATE_TO_HUMAN]" in bot_response_english:
        needs_human = True
        trigger_human_handoff(db, sender_number)
        bot_response_english = bot_response_english.replace("[ESCALATE_TO_HUMAN]", "").strip()

    # Step 4: Translate the secure response back to the original language
    final_bot_response = translate_from_english(bot_response_english, detected_lang)

    # Update session history (Storing English maintains the AI context perfectly)
    append_to_history(db, sender_number, "user", english_msg)
    append_to_history(db, sender_number, "assistant", bot_response_english)

    # Respond to Twilio
    resp = MessagingResponse()
    resp.message(final_bot_response)

    
    return Response(content=str(resp), media_type="application/xml")
