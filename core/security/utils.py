from __future__ import annotations
import secrets
import string

def generate_numeric_code(length: int = 6) -> str:
    if length < 4:
        raise ValueError("Code length must be at least 4.")

    return "".join(secrets.choice(string.digits) for _ in range(length))


def generate_secure_token(length: int = 32) -> str:
    if length < 16:
        raise ValueError("Token length must be at least 16.")

    return secrets.token_urlsafe(length)