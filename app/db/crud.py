from sqlalchemy.orm import Session
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

def get_escalated_queues(db: Session):
    """Fetch all users who are currently flagged for human intervention."""
    escalated_users = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.is_escalated == True).all()
    queue = []
    
    for user in escalated_users:
        messages = db.query(models.ChatMessage).filter(models.ChatMessage.user_id == user.id).order_by(models.ChatMessage.timestamp.asc()).all()
        history = [{"role": msg.role, "content": msg.content} for msg in messages]
        queue.append({
            "phone_number": user.phone_number,
            "history": history
        })
        
    return queue
