from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db import models
from datetime import datetime

# --- WhatsApp Users ---

def get_or_create_user(db: Session, phone_number: str) -> models.WhatsAppUser:
    user = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.phone_number == phone_number).first()
    if not user:
        user = models.WhatsAppUser(phone_number=phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def set_user_escalation(db: Session, phone_number: str, is_escalated: bool):
    user = get_or_create_user(db, phone_number)
    user.is_escalated = is_escalated
    db.commit()

# --- Chat History ---

def add_message(db: Session, phone_number: str, role: str, content: str):
    user = get_or_create_user(db, phone_number)
    message = models.ChatMessage(user_id=user.id, role=role, content=content)
    db.add(message)
    db.commit()
    return message

def get_chat_history(db: Session, phone_number: str, limit: int = 20):
    user = get_or_create_user(db, phone_number)
    messages = db.query(models.ChatMessage).filter(models.ChatMessage.user_id == user.id).order_by(models.ChatMessage.timestamp.asc()).limit(limit).all()
    
    # Format to match Groq's expected input style
    return [{"role": msg.role, "content": msg.content} for msg in messages]

def clear_chat_history(db: Session, phone_number: str):
    user = get_or_create_user(db, phone_number)
    db.query(models.ChatMessage).filter(models.ChatMessage.user_id == user.id).delete()
    db.commit()

# --- Mentors ---

def get_mentor_by_email(db: Session, email: str):
    return db.query(models.Mentor).filter(models.Mentor.email == email).first()

def get_escalated_queues(db: Session, mentor_id: int = None):
    """Fetch all users currently flagged for human intervention, including claim status."""
    query = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.is_escalated == True)
    
    if mentor_id:
        # Show users that are either UNCLAIMED or claimed by THIS specific mentor
        query = query.filter(or_(
            models.WhatsAppUser.claimed_by_mentor_id == None,
            models.WhatsAppUser.claimed_by_mentor_id == mentor_id
        ))
        
    escalated_users = query.all()
    queue = []
    for user in escalated_users:
        messages = db.query(models.ChatMessage).filter(models.ChatMessage.user_id == user.id).order_by(models.ChatMessage.timestamp.asc()).all()
        history = [{"role": msg.role, "content": msg.content} for msg in messages]
        queue.append({
            "phone_number": user.phone_number,
            "history": history,
            "claimed_by_mentor_id": user.claimed_by_mentor_id,
            "claimed_by_name": user.claimed_by.name if user.claimed_by else None,
            "claimed_at": user.claimed_at.isoformat() if user.claimed_at else None,
        })
    return queue

def claim_user_for_mentor(db: Session, phone_number: str, mentor_id: int) -> bool:
    """Try to claim a user for a mentor. Returns True if successful, False if already claimed by someone else."""
    user = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.phone_number == phone_number).first()
    if not user:
        return False
    # Already claimed by this mentor – OK
    if user.claimed_by_mentor_id == mentor_id:
        return True
    # Already claimed by a different mentor – refuse
    if user.claimed_by_mentor_id is not None:
        return False
    # Unclaimed – claim it
    user.claimed_by_mentor_id = mentor_id
    user.claimed_at = datetime.utcnow()
    db.commit()
    return True

def release_claim(db: Session, phone_number: str):
    """Release the claim on a user, clearing both escalation and claim."""
    user = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.phone_number == phone_number).first()
    if user:
        user.claimed_by_mentor_id = None
        user.claimed_at = None
        user.is_escalated = False
        db.commit()
def get_pending_mentors(db: Session):
    """Fetch all mentors who are waiting for admin approval."""
    return db.query(models.Mentor).filter(models.Mentor.is_approved == False).all()

def approve_mentor(db: Session, mentor_id: int):
    """Approve a mentor by their ID."""
    mentor = db.query(models.Mentor).filter(models.Mentor.id == mentor_id).first()
    if mentor:
        mentor.is_approved = True
        db.commit()
        db.refresh(mentor)
    return mentor

def delete_mentor(db: Session, mentor_id: int):
    """Reject/Delete a mentor application."""
    mentor = db.query(models.Mentor).filter(models.Mentor.id == mentor_id).first()
    if mentor:
        db.delete(mentor)
        db.commit()
        return True
    return False
