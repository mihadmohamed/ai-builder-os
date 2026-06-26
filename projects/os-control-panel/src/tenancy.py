from __future__ import annotations

from contextvars import ContextVar, Token
import hashlib
import re


_ACTIVE_USER_ID: ContextVar[str] = ContextVar("ai_builder_os_active_user_id", default="")
_ACTIVE_USER_LABEL: ContextVar[str] = ContextVar("ai_builder_os_active_user_label", default="")


def normalize_user_id(value: str) -> str:
    raw = value.strip().lower()
    if not raw:
        return ""
    readable = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")[:48] or "user"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"{readable}-{digest}"


def active_user_id() -> str:
    return _ACTIVE_USER_ID.get()


def active_user_label() -> str:
    return _ACTIVE_USER_LABEL.get()


def set_active_user(value: str) -> tuple[Token[str], Token[str]]:
    normalized = normalize_user_id(value)
    label = value.strip().lower()
    return (_ACTIVE_USER_ID.set(normalized), _ACTIVE_USER_LABEL.set(label))


def reset_active_user(token: tuple[Token[str], Token[str]]) -> None:
    id_token, label_token = token
    _ACTIVE_USER_ID.reset(id_token)
    _ACTIVE_USER_LABEL.reset(label_token)
