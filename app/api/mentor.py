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
    On first reply, automatically claims the client for this mentor.
    Rejects if another mentor already claimed this client.
    """
    # 1. Verify the session is actually in 'needs_human' state
    if not is_human_handoff_active(db, request.phone_number):
        raise HTTPException(status_code=400, detail="This user is not currently flagged for human intervention.")

    # 2. Try to claim the client (call-centre style)
    claimed = crud.claim_user_for_mentor(db, request.phone_number, current_mentor.id)
    if not claimed:
        # Already claimed by someone else — find out who
        user = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.phone_number == request.phone_number).first()
        claimant = user.claimed_by.name if user and user.claimed_by else "another counselor"
        raise HTTPException(
            status_code=409,
            detail=f"This client has already been claimed by {claimant}. They are handling this case."
        )

    try:
        # 3. Send the WhatsApp message via Twilio REST API
        sender_id = settings.TWILIO_WHATSAPP_NUMBER
        if not sender_id.startswith("whatsapp:"):
            sender_id = f"whatsapp:{sender_id}"

        message = twilio_client.messages.create(
            body=request.message,
            from_=sender_id,
            to=request.phone_number
        )

        # 4. Log the mentor's message in the session history under their name
        append_to_history(db, request.phone_number, f"assistant (mentor: {current_mentor.name})", request.message)

        # 5. Release if requested
        if request.resolve_session:
            crud.release_claim(db, request.phone_number)

        return {"status": "success", "message_sid": message.sid, "session_resolved": request.resolve_session}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to send mentor reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resolve/{phone_number:path}")
async def resolve_case(
    phone_number: str,
    db: Session = Depends(get_db),
    current_mentor: models.Mentor = Depends(security.get_current_mentor)
):
    """Release a claimed client and return them to the AI queue (or remove from queue)."""
    user = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.phone_number == phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    # Only the mentor who claimed them can release
    if user.claimed_by_mentor_id and user.claimed_by_mentor_id != current_mentor.id:
        raise HTTPException(status_code=403, detail="You did not claim this client.")
    crud.release_claim(db, phone_number)
    resolve_human_handoff(db, phone_number)
    return {"status": "released"}


@router.get("/queue")
async def get_mentor_queue(
    db: Session = Depends(get_db),
    current_mentor: models.Mentor = Depends(security.get_current_mentor)
):
    """Returns a list of all phone numbers currently flagged for human intervention from the DB."""
    queue = crud.get_escalated_queues(db)
    return {"active_escalations": queue}

@router.get("/me/stats")
async def get_my_stats(
    db: Session = Depends(get_db),
    current_mentor: models.Mentor = Depends(security.get_current_mentor)
):
    """Returns personal performance stats for the logged-in mentor."""
    pattern = f"assistant (mentor: {current_mentor.name})"
    sessions = db.query(models.ChatMessage).filter(models.ChatMessage.role == pattern).count()
    clients = db.query(models.ChatMessage.user_id).filter(models.ChatMessage.role == pattern).distinct().count()
    active = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.is_escalated == True).count()
    return {
        "mentor_id": current_mentor.id,
        "name": current_mentor.name,
        "specialization": current_mentor.specialization or "Counselor",
        "sessions_handled": sessions,
        "clients_served": clients,
        "active_escalations": active,
        "is_admin": current_mentor.is_admin
    }
