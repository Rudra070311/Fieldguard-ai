from __future__ import annotations
from dataclasses import dataclass
from html import escape

@dataclass(frozen=True)
class EmailTemplate:
    subject: str
    text: str
    html: str

def verification_email(verification_url: str,) -> EmailTemplate:
    safe_url = escape(verification_url)

    return EmailTemplate(
        subject="Verify your iDeez email",
        text=(
            "Please verify your email address by opening "
            f"this link:\n\n{verification_url}\n\n"
            "If you did not request this, you can ignore this email."
        ),
        html=f"""
        <html>
            <body>
                <h2>Verify your email</h2>
                <p>
                    Please verify your email address to continue.
                </p>
                <p>
                    <a href="{safe_url}">
                        Verify email
                    </a>
                </p>
                <p>
                    If you did not request this, you can ignore
                    this email.
                </p>
            </body>
        </html>
        """,
    )

def otp_email(otp: str,) -> EmailTemplate:
    return EmailTemplate(
        subject="Your iDeez verification code",
        text=(
            f"Your verification code is: {otp}\n\n"
            "Do not share this code with anyone."
        ),
        html=f"""
        <html>
            <body>
                <h2>Your verification code</h2>
                <p>Your iDeez verification code is:</p>
                <h1>{escape(otp)}</h1>
                <p>
                    Do not share this code with anyone.
                </p>
            </body>
        </html>
        """,
    )

def magic_link_email(magic_link_url: str,) -> EmailTemplate:
    safe_url = escape(magic_link_url)

    return EmailTemplate(
        subject="Your iDeez sign-in link",
        text=(
            "Use the following link to continue signing in:\n\n"
            f"{magic_link_url}\n\n"
            "If you did not request this link, ignore this email."
        ),
        html=f"""
        <html>
            <body>
                <h2>Sign in to iDeez</h2>
                <p>
                    Click the button below to continue.
                </p>
                <p>
                    <a href="{safe_url}">
                        Continue to iDeez
                    </a>
                </p>
                <p>
                    If you did not request this link, ignore this email.
                </p>
            </body>
        </html>
        """,
    )