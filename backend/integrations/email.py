import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str = "noreply@freightgpt.local",
        cc: Optional[List[str]] = None,
    ) -> bool:
        """Send email via SMTP (FREE: Gmail SMTP or any SMTP server)."""
        # If SMTP not configured, log it gracefully
        if not self.smtp_user or not self.smtp_password:
            logger.info(f"[EMAIL MOCK] To: {to_email}, Subject: {subject}")
            logger.info(f"[EMAIL MOCK] Body: {body[:200]}...")
            return True  # Don't fail - just log in dev mode

        try:
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            if cc:
                msg["Cc"] = ", ".join(cc)
            msg.attach(MIMEText(body, "html"))

            all_recipients = [to_email] + (cc or [])

            # Use async SMTP
            import asyncio
            loop = asyncio.get_event_loop()

            def send():
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(from_email, all_recipients, msg.as_string())

            await loop.run_in_executor(None, send)
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


email_service = EmailService()
