from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db import models
from app.core import security
import csv, io
from datetime import datetime, timezone
from pydantic import BaseModel

class RejectReason(BaseModel):
    reason: str = ""

router = APIRouter()

@router.get("/stats")
async def get_admin_statistics(
    period: str = "all", # all | today | week | month
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """Returns aggregated system usage statistics based on a timeline."""
    from datetime import timedelta, timezone
    now = datetime.now(timezone.utc)
    
    if period == "today":
        cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        cutoff = now - timedelta(days=7)
    elif period == "month":
        cutoff = now - timedelta(days=30)
    else:
        cutoff = None
        
    def msg_q():
        q = db.query(models.ChatMessage)
        if cutoff:
            q = q.filter(models.ChatMessage.timestamp >= cutoff)
        return q
        
    def user_q():
        q = db.query(models.WhatsAppUser)
        if cutoff:
            q = q.filter(models.WhatsAppUser.created_at >= cutoff)
        return q

    total_users = user_q().count()
    total_messages = msg_q().count()
    total_ai_responses = msg_q().filter(models.ChatMessage.role == 'assistant').count()
    active_escalations = db.query(models.WhatsAppUser).filter(models.WhatsAppUser.is_escalated == True).count()
    total_mentors = db.query(models.Mentor).filter(models.Mentor.is_approved == True).count()
    
    return {
        "admin": {"name": admin.name},
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
            "id": m.id, "name": m.name, "email": m.email,
            "phone": m.phone_number, "specialization": m.specialization,
            "experience": m.experience_years, "bio": m.bio,
            "license": m.license_number, "created_at": m.created_at
        }
        for m in pending
    ]

@router.get("/mentors")
async def get_all_approved_mentors(
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """List all approved mentors with their performance stats."""
    approved = db.query(models.Mentor).filter(
        models.Mentor.is_approved == True,
        models.Mentor.is_admin == False
    ).all()

    result = []
    for m in approved:
        # Count how many mentor messages they've sent (role contains mentor name)
        mentor_role_pattern = f"assistant (mentor: {m.name})"
        sessions_handled = db.query(models.ChatMessage).filter(
            models.ChatMessage.role == mentor_role_pattern
        ).count()

        # Count distinct users they've responded to
        distinct_users = db.query(models.ChatMessage.user_id).filter(
            models.ChatMessage.role == mentor_role_pattern
        ).distinct().count()

        result.append({
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "phone": m.phone_number,
            "specialization": m.specialization or "General Counseling",
            "experience": m.experience_years or 0,
            "license": m.license_number,
            "bio": m.bio,
            "joined": m.created_at,
            "sessions_handled": sessions_handled,
            "clients_served": distinct_users,
        })

    return result

@router.post("/approve-mentor/{mentor_id}")
async def approve_counselor(
    mentor_id: int,
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """Approve a counselor application."""
    from app.db import crud
    from app.core.notifications import notifier

    mentor = crud.approve_mentor(db, mentor_id)
    if mentor:
        notifier.send_mentor_approval_email(mentor.email, mentor.name)

    return {"status": "success", "message": f"Mentor {mentor.name} approved."}

@router.post("/reject-mentor/{mentor_id}")
async def reject_counselor(
    mentor_id: int,
    payload: RejectReason,
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """Reject and delete a counselor application."""
    from app.db import crud
    from app.core.notifications import notifier

    mentor = db.query(models.Mentor).filter(models.Mentor.id == mentor_id).first()
    if mentor:
        notifier.send_mentor_rejection_email(mentor.email, mentor.name, payload.reason)

    crud.delete_mentor(db, mentor_id)
    return {"status": "success", "message": "Mentor application rejected."}

@router.delete("/mentors/{mentor_id}")
async def remove_mentor(
    mentor_id: int,
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """Remove an approved mentor from the system."""
    mentor = db.query(models.Mentor).filter(models.Mentor.id == mentor_id).first()
    if not mentor:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Mentor not found.")
    db.delete(mentor)
    db.commit()
    return {"status": "success", "message": f"{mentor.name} has been removed from the system."}

@router.get("/download-report")
async def download_metrics_report(
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin),
    period: str = "all"  # all | today | week | month
):
    """Generate and download a filtered CSV metrics report."""
    from datetime import timedelta

    now = datetime.now(timezone.utc)

    # Compute date cutoff based on period
    if period == "today":
        cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = f"Today ({now.strftime('%d %b %Y')})"
    elif period == "week":
        cutoff = now - timedelta(days=7)
        period_label = f"Last 7 Days ({cutoff.strftime('%d %b')} – {now.strftime('%d %b %Y')})"
    elif period == "month":
        cutoff = now - timedelta(days=30)
        period_label = f"Last 30 Days ({cutoff.strftime('%d %b')} – {now.strftime('%d %b %Y')})"
    else:
        cutoff = None
        period_label = "All Time"

    def msg_q():
        q = db.query(models.ChatMessage)
        if cutoff:
            q = q.filter(models.ChatMessage.timestamp >= cutoff)
        return q

    def user_q():
        q = db.query(models.WhatsAppUser)
        if cutoff:
            q = q.filter(models.WhatsAppUser.created_at >= cutoff)
        return q

    output = io.StringIO()
    writer = csv.writer(output)

    # === HEADER ===
    writer.writerow(["JOOTRH GBV & Mental Health Support System – Metrics Report"])
    writer.writerow([f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}"])
    writer.writerow([f"Period: {period_label}"])
    writer.writerow([])

    # === SYSTEM OVERVIEW ===
    writer.writerow(["SYSTEM OVERVIEW"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Users Reached (period)", user_q().count()])
    writer.writerow(["Messages Processed (period)", msg_q().count()])
    writer.writerow(["AI Triage Responses (period)", msg_q().filter(models.ChatMessage.role == 'assistant').count()])
    writer.writerow(["Active Emergencies (live)", db.query(models.WhatsAppUser).filter(models.WhatsAppUser.is_escalated == True).count()])
    writer.writerow(["Active Counselors", db.query(models.Mentor).filter(models.Mentor.is_approved == True, models.Mentor.is_admin == False).count()])
    writer.writerow([])

    # === COUNSELOR PERFORMANCE ===
    writer.writerow(["COUNSELOR PERFORMANCE"])
    writer.writerow(["Name", "Email", "Specialization", "Experience (Yrs)", "Sessions in Period", "Unique Clients in Period", "Date Joined"])

    approved = db.query(models.Mentor).filter(
        models.Mentor.is_approved == True, models.Mentor.is_admin == False
    ).all()

    for m in approved:
        pattern = f"assistant (mentor: {m.name})"
        q = db.query(models.ChatMessage).filter(models.ChatMessage.role == pattern)
        if cutoff:
            q = q.filter(models.ChatMessage.timestamp >= cutoff)
        sessions = q.count()
        clients_q = db.query(models.ChatMessage.user_id).filter(models.ChatMessage.role == pattern)
        if cutoff:
            clients_q = clients_q.filter(models.ChatMessage.timestamp >= cutoff)
        clients = clients_q.distinct().count()
        writer.writerow([
            m.name, m.email, m.specialization or "N/A",
            m.experience_years or 0, sessions, clients,
            m.created_at.strftime("%Y-%m-%d") if m.created_at else "N/A"
        ])

    writer.writerow([])

    # === USER ENGAGEMENT ===
    writer.writerow(["USER ENGAGEMENT BREAKDOWN"])
    writer.writerow(["Phone Number", "Total Messages", "AI Responses", "Mentor Responses", "First Seen"])

    users = db.query(models.WhatsAppUser).all()
    for u in users:
        base = db.query(models.ChatMessage).filter(models.ChatMessage.user_id == u.id)
        if cutoff:
            base = base.filter(models.ChatMessage.timestamp >= cutoff)
        total = base.count()
        if total == 0 and cutoff:
            continue  # skip users with no activity in the period
        ai = base.filter(models.ChatMessage.role == 'assistant').count()
        mentor_msgs = db.query(models.ChatMessage).filter(
            models.ChatMessage.user_id == u.id,
            models.ChatMessage.role.like('%mentor%')
        )
        if cutoff:
            mentor_msgs = mentor_msgs.filter(models.ChatMessage.timestamp >= cutoff)
        writer.writerow([
            u.phone_number.replace("whatsapp:", ""),
            total, ai, mentor_msgs.count(),
            u.created_at.strftime("%Y-%m-%d") if u.created_at else "N/A"
        ])

    output.seek(0)
    period_slug = period.replace(" ", "_")
    filename = f"jootrh_{period_slug}_report_{now.strftime('%Y%m%d_%H%M')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"; filename*=UTF-8''{filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@router.get("/download-mentors")
async def download_mentors_report(
    db: Session = Depends(get_db),
    admin: models.Mentor = Depends(security.get_current_active_admin)
):
    """Generate and download a CSV of approved counselors."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    now = datetime.now(timezone.utc)
    writer.writerow(["Counselor Team Export"])
    writer.writerow([f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}"])
    writer.writerow([])
    writer.writerow(["Name", "Email", "Phone Number", "Specialization", "Experience (Yrs)", "License", "Date Joined"])
    
    approved = db.query(models.Mentor).filter(
        models.Mentor.is_approved == True, models.Mentor.is_admin == False
    ).all()
    
    for m in approved:
        writer.writerow([
            m.name, m.email, m.phone_number or "N/A", m.specialization or "N/A",
            m.experience_years or 0, m.license_number or "N/A",
            m.created_at.strftime("%Y-%m-%d") if m.created_at else "N/A"
        ])
        
    output.seek(0)
    filename = f"jootrh_mentors_{now.strftime('%Y%m%d_%H%M')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"; filename*=UTF-8''{filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
