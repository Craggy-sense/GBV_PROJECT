import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import List

class EmailNotifier:
    def __init__(self):
        # We can look for SMTP settings, if they don't exist we use "mock" mode
        self.smtp_host = getattr(settings, "SMTP_HOST", None)
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_user = getattr(settings, "SMTP_USER", None)
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", None)
        self.from_email = getattr(settings, "SMTP_FROM_EMAIL", "noreply@jootrh.local")
        self.is_mock = not (self.smtp_host and self.smtp_user and self.smtp_password)

    def _send_email(self, to_email: str, subject: str, text_body: str):
        if self.is_mock:
            print("\n" + "="*60)
            print(f"📧 MOCK EMAIL NOTIFICATION")
            print(f"To: {to_email}")
            print(f"From: {self.from_email}")
            print(f"Subject: {subject}")
            print("-" * 60)
            print(text_body.strip())
            print("="*60 + "\n")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(text_body, 'plain'))

            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.set_debuglevel(0)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")

    def send_mentor_approval_email(self, mentor_email: str, mentor_name: str):
        subject = "Your Counselor Account has been Approved"
        body = f"""Hello {mentor_name},

Your counselor account for the JooTRH GBV & Mental Health Triage system has been approved. You can now log in to the mentor dashboard to start assisting clients in need.

System Login: http://localhost:8000/mentor

Thank you for volunteering your time.

Best,
The JooTRH Admin Team"""
        self._send_email(mentor_email, subject, body)

    def send_mentor_rejection_email(self, mentor_email: str, mentor_name: str, reason: str = ""):
        subject = "Update on Your Counselor Application"
        body = f"""Hello {mentor_name},

Thank you for applying to be a counselor for the JooTRH GBV & Mental Health Triage system. Unfortunately, your application has not been approved at this time.
"""
        if reason:
            body += f"\nReason provided by administration: {reason}\n"
        body += """
If you have any questions, please contact administration.

Best,
The JooTRH Admin Team"""
        self._send_email(mentor_email, subject, body)

    def send_emergency_alert(self, mentor_emails: List[str], client_phone: str):
        subject = "URGENT: New Escalation in Triage Queue"
        body = f"""Attention Counselors,

A new client ({client_phone}) has requested immediate human assistance via the WhatsApp Triage Bot.

Please log in to the counselor dashboard to review and claim this case. First counselor to reply will claim the client.

Dashboard URL: http://localhost:8000/mentor

Best,
JooTRH Automated Triage"""
        for email in mentor_emails:
            self._send_email(email, subject, body)

notifier = EmailNotifier()
