from __future__ import annotations
import hmac

def safe_compare(value_a: str, value_b: str) -> bool:
    if not isinstance(value_a, str) or not isinstance(value_b, str):
        return False

    return hmac.compare_digest(value_a, value_b,)