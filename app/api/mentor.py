from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from twilio.rest import Client
from app.core.config import settings
from app.core import security
from app.db import models, crud
from app.db.database import get_db
from app.chatbot.session import is_human_handoff_active, get_session_history, resolve_human_handoff, append_to_history

router = APIRouter()

class MentorReplyRequest(BaseModel):
    phone_number: str
    message: str
    resolve_session: bool = False # If true, hands control back to AI after sending

def get_twilio_client():
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="Twilio credentials not configured")
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

@router.post("/reply")
async def send_mentor_reply(
    request: MentorReplyRequest,
    twilio_client: Client = Depends(get_twilio_client),
    db: Session = Depends(get_db),
    current_mentor: models.Mentor = Depends(security.get_current_mentor)
):
    """
    Endpoint for an authenticated human mentor to send a manual reply.
    """
    # 1. Verify the session is actually in 'needs_human' state
    if not is_human_handoff_active(db, request.phone_number):
        raise HTTPException(status_code=400, detail="This user is not currently flagged for human intervention.")
        
    try:
        # 2. Send the WhatsApp message via Twilio REST API
        sender_id = settings.TWILIO_WHATSAPP_NUMBER
        if not sender_id.startswith("whatsapp:"):
            sender_id = f"whatsapp:{sender_id}"
            
        message = twilio_client.messages.create(
            body=request.message,
            from_=sender_id,
            to=request.phone_number
        )
        
        # 3. Log the mentor's message in the session history under their name
        append_to_history(db, request.phone_number, f"assistant (mentor: {current_mentor.name})", request.message)
        
        # 4. Release lock if requested
        if request.resolve_session:
            resolve_human_handoff(db, request.phone_number)
            
        return {"status": "success", "message_sid": message.sid, "session_resolved": request.resolve_session}
        
    except Exception as e:
        print(f"Failed to send mentor reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue")
async def get_mentor_queue(
    db: Session = Depends(get_db),
    current_mentor: models.Mentor = Depends(security.get_current_mentor)
):
    """Returns a list of all phone numbers currently flagged for human intervention from the DB."""
    queue = crud.get_escalated_queues(db)
    return {"active_escalations": queue}
