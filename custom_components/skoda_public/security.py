"""Redact vehicle identifiers and credentials from error text."""
from __future__ import annotations


def redact_sensitive(text: str, *secrets: str | None) -> str:
    """Replace configured secrets before exposing API error details."""
    result = text
    for secret in secrets:
        if secret and len(secret) >= 4:
            result = result.replace(secret, "[REDACTED]")
    return result
