#!/usr/bin/env python3
"""Utilities for secure handling of API keys and secrets.

This module provides safeguards against accidental logging of sensitive values.
"""

import re
from typing import Optional


class SecretString:
    """A string wrapper that prevents accidental exposure in logs/prints.

    When printed or converted to string representation, shows "[REDACTED]"
    instead of the actual value. Use .get() to access the real value.

    Example:
        api_key = SecretString(os.environ.get("FREEPLAY_API_KEY"))
        print(api_key)  # Output: [REDACTED]
        headers = {"Authorization": f"Bearer {api_key.get()}"}  # Uses real value
    """

    def __init__(self, value: Optional[str]):
        self._value = value

    def get(self) -> Optional[str]:
        """Get the actual secret value."""
        return self._value

    def __str__(self) -> str:
        return "[REDACTED]" if self._value else ""

    def __repr__(self) -> str:
        return "SecretString([REDACTED])" if self._value else "SecretString(None)"

    def __bool__(self) -> bool:
        return bool(self._value)


# Common patterns for API keys and secrets
_SECRET_PATTERNS = [
    # Bearer tokens in headers
    (re.compile(r'(Bearer\s+)[A-Za-z0-9_\-\.]+', re.IGNORECASE), r'\1[REDACTED]'),
    # Authorization headers
    (re.compile(r'(Authorization["\']?\s*:\s*["\']?)[^"\'}\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    # API key patterns (common formats)
    (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)[A-Za-z0-9_\-\.]+', re.IGNORECASE), r'\1[REDACTED]'),
    # Generic secret/token patterns
    (re.compile(r'(secret["\']?\s*[:=]\s*["\']?)[A-Za-z0-9_\-\.]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(token["\']?\s*[:=]\s*["\']?)[A-Za-z0-9_\-\.]+', re.IGNORECASE), r'\1[REDACTED]'),
    # Freeplay specific patterns
    (re.compile(r'(FREEPLAY_API_KEY\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
]


def redact_secrets(text: str) -> str:
    """Remove potential secrets from text before logging.

    Applies pattern matching to redact common secret formats including:
    - Bearer tokens
    - Authorization headers
    - API keys
    - Tokens and secrets

    Args:
        text: The text that may contain secrets

    Returns:
        Text with secrets replaced by [REDACTED]
    """
    result = text
    for pattern, replacement in _SECRET_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def safe_error_message(response_text: str, max_length: int = 500) -> str:
    """Create a safe error message from an API response.

    Redacts potential secrets and truncates long responses.

    Args:
        response_text: The raw response text
        max_length: Maximum length of the output

    Returns:
        Safe, truncated error message
    """
    redacted = redact_secrets(response_text)
    if len(redacted) > max_length:
        return redacted[:max_length] + "... [truncated]"
    return redacted
