"""Profile PII redaction helpers for the TJU MCP server.

By default the MCP server masks sensitive profile fields so that the AI agent
cannot read the user's student ID, contact details, or home address — even
through a prompt-injection attack.  Revealing these fields requires a
**server-side** configuration flag (``config.toml [preferences]
mcp_reveal_pii = true`` or the ``TJU_MCP_REVEAL_PII=1`` environment
variable) and is *never* controlled by a tool argument.
"""

from __future__ import annotations

import os
from typing import Any

# Fields that are masked unless mcp_reveal_pii is enabled.
SENSITIVE_FIELDS: frozenset[str] = frozenset(
    {
        "stu_id",      # student ID — partial mask
        "email",
        "phone",
        "mobile",
        "home_phone",
        "home_address",
        "home_address_zip",
        # Graduate-specific identifiers / supervisory contacts sometimes contain PII
        "cooperative_unit",
        "orientation_unit",
        "address",     # contact address
    }
)


def _partial_mask(value: str) -> str:
    """Return a partially masked version of *value*.

    Examples::

        "2021000007"  →  "2021****07"
        "13812345678" →  "138****5678"
        "hi@foo.com"  →  "hi@***"
        "abc"         →  "***"
    """
    if not isinstance(value, str) or len(value) <= 4:
        return "***"
    keep = max(2, len(value) // 5)
    prefix = value[:keep]
    suffix = value[-keep:]
    stars = "*" * max(4, len(value) - 2 * keep)
    return f"{prefix}{stars}{suffix}"


def mask_profile(data: dict[str, Any], reveal: bool = False) -> dict[str, Any]:
    """Return a copy of the serialised profile dict with PII fields masked.

    Args:
        data:   Serialised :class:`~tju.models.profile.Profile` dict.
        reveal: If ``True`` all fields are returned as-is.  This should only
                be set from the server-side config, never from a tool argument.

    Returns:
        A new dict; sensitive fields have their values replaced by a partial
        mask string.  Non-sensitive fields are unchanged.
    """
    if reveal:
        return dict(data)

    result: dict[str, Any] = {}
    for key, value in data.items():
        if key in SENSITIVE_FIELDS and value is not None:
            result[key] = _partial_mask(str(value)) if value else value
        else:
            result[key] = value
    return result


def should_reveal_pii() -> bool:
    """Return ``True`` if PII fields should be returned unmasked.

    Reads (in order of priority):
    1. ``TJU_MCP_REVEAL_PII`` environment variable (``1`` / ``true`` / ``yes``).
    2. ``[preferences] mcp_reveal_pii`` in ``config.toml``.
    """
    env_val = os.environ.get("TJU_MCP_REVEAL_PII", "").lower()
    if env_val in {"1", "true", "yes"}:
        return True
    if env_val in {"0", "false", "no"}:
        return False

    # Fall back to config file
    try:
        from tju.config import get_preferences  # noqa: PLC0415
        return bool(get_preferences().get("mcp_reveal_pii", False))
    except Exception:  # noqa: BLE001
        return False
