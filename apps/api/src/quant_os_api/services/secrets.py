"""Secret helpers — Fernet encryption when ENCRYPTION_KEY is set."""

from __future__ import annotations

import base64
import hashlib
import os
from typing import Any


def _fernet():
    key = os.getenv("ENCRYPTION_KEY", "").strip()
    if not key:
        return None
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        return None
    # Derive 32-byte urlsafe key from provided secret
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(plaintext: str) -> dict[str, Any]:
    f = _fernet()
    if f is None:
        return {
            "encrypted": False,
            "value": plaintext,
            "message": "ENCRYPTION_KEY unset or cryptography missing — stored plaintext marker only",
        }
    token = f.encrypt(plaintext.encode("utf-8")).decode("utf-8")
    return {"encrypted": True, "value": token}


def decrypt_secret(token: str) -> dict[str, Any]:
    f = _fernet()
    if f is None:
        return {"encrypted": False, "value": token}
    try:
        return {"encrypted": True, "value": f.decrypt(token.encode("utf-8")).decode("utf-8")}
    except Exception as exc:  # noqa: BLE001
        return {"encrypted": True, "error": str(exc), "value": None}
