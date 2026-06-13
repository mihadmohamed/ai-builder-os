from __future__ import annotations

from contextvars import ContextVar, Token
import hashlib
import re


_ACTIVE_USER_ID: ContextVar[str] = ContextVar("ai_builder_os_active_user_id", default="")


def normalize_user_id(value: str) -> str:
    raw = value.strip().lower()
    if not raw:
        return ""
    readable = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")[:48] or "user"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"{readable}-{digest}"


def active_user_id() -> str:
    return _ACTIVE_USER_ID.get()


def set_active_user(value: str) -> Token[str]:
    return _ACTIVE_USER_ID.set(normalize_user_id(value))


def reset_active_user(token: Token[str]) -> None:
    _ACTIVE_USER_ID.reset(token)

