from __future__ import annotations
import logging
from email.message import EmailMessage
from typing import Optional
import aiosmtplib
from config.settings import Settings

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def send(self, to: str, subject: str, body: str, *, html: Optional[str] = None,) -> None:
        if not to:
            raise ValueError("Recipient email is required.")
        if not subject:
            raise ValueError("Email subject is required.")

        message = EmailMessage()
        message["From"] = self.settings.email.sender
        message["To"] = to
        message["Subject"] = subject

        message.set_content(body)

        if html:
            message.add_alternative(html, subtype="html",)

        if not self.settings.email.smtp_host:
            logger.warning("SMTP is not configured; email was not sent.")
            return

        await aiosmtplib.send(
            message,
            hostname=self.settings.email.smtp_host,
            port=self.settings.email.smtp_port,
            username=(self.settings.email.username if self.settings.email.username else None),
            password=(self.settings.email.password.get_secret_value() if self.settings.email.password else None),
            start_tls=self.settings.email.use_tls,
        )

    async def send_verification_email(self, email: str, verification_url: str,) -> None:
        from .templates import (verification_email,)
        template = verification_email(verification_url=verification_url,)

        await self.send(
            email,
            template.subject,
            template.text,
            html=template.html,
        )

    async def send_otp(self, email: str, otp: str,) -> None:
        from .templates import otp_email
        template = otp_email(otp)

        await self.send(
            email,
            template.subject,
            template.text,
            html=template.html,
        )

    async def send_magic_link(self, email: str, magic_link_url: str,) -> None:
        from .templates import magic_link_email
        template = magic_link_email(magic_link_url=magic_link_url,)

        await self.send(
            email,
            template.subject,
            template.text,
            html=template.html,
        )