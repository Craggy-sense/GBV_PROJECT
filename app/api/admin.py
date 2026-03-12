from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db import models
from app.core import security

router = APIRouter()

@router.get("/stats")
async def get_admin_statistics(
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """
    Returns aggregated system usage statistics.
    Requires the authenticated user to have `is_admin = True`.
    """
    # Total Users
    total_users = db.query(models.WhatsAppUser).count()
    
    # Total Messages Processed
    total_messages = db.query(models.ChatMessage).count()
    
    # Total AI Responses (Messages sent by 'assistant')
    total_ai_responses = db.query(models.ChatMessage).filter(models.ChatMessage.role == 'assistant').count()
    
    # Total Active Emergencies
    active_escalations = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.is_escalated == True).count()
    
    # Total Mentor Accounts
    total_mentors = db.query(models.Mentor).count()
    
    return {
        "metrics": {
            "total_users": total_users,
            "total_messages_processed": total_messages,
            "total_ai_triage_responses": total_ai_responses,
            "active_emergencies": active_escalations,
            "registered_counselors": total_mentors
        }
    }
@router.get("/pending-mentors")
async def get_pending_counselors(
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """List all mentors awaiting approval."""
    from app.db import crud
    pending = crud.get_pending_mentors(db)
    return [
        {
            "id": m.id, 
            "name": m.name, 
            "email": m.email, 
            "phone": m.phone_number, 
            "specialization": m.specialization,
            "experience": m.experience_years,
            "bio": m.bio,
            "license": m.license_number,
            "created_at": m.created_at
        } 
        for m in pending
    ]

@router.post("/approve-mentor/{mentor_id}")
async def approve_counselor(
    mentor_id: int,
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """Approve a counselor application."""
    from app.db import crud
    mentor = crud.approve_mentor(db, mentor_id)
    return {"status": "success", "message": f"Mentor {mentor.name} approved."}

@router.post("/reject-mentor/{mentor_id}")
async def reject_counselor(
    mentor_id: int,
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """Reject and delete a counselor application."""
    from app.db import crud
    success = crud.delete_mentor(db, mentor_id)
    return {"status": "success", "message": "Mentor application rejected."}
