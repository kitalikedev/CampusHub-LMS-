"""Mật khẩu (BR-ACC-03, 05; NFR-SEC-02) và JWT."""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from src.core.config import settings

ALGORITHM = "HS256"
# Bỏ các ký tự dễ nhầm: 0/O, 1/l/I (BR-ACC-03).
_LETTERS = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"
_DIGITS = "23456789"
MIN_PASSWORD_BYTES = 8
MAX_PASSWORD_BYTES = 72  # giới hạn của bcrypt (ISS-07)


def password_length_ok(password: str) -> bool:
    size = len(password.encode("utf-8"))
    return MIN_PASSWORD_BYTES <= size <= MAX_PASSWORD_BYTES


def hash_password(password: str) -> str:
    raw = password.encode("utf-8")
    if len(raw) > MAX_PASSWORD_BYTES:
        raise ValueError("password longer than 72 bytes")
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    raw = password.encode("utf-8")
    if len(raw) > MAX_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(raw, password_hash.encode("utf-8"))
    except ValueError:
        return False


def generate_temp_password(length: int = 12) -> str:
    alphabet = _LETTERS + _DIGITS
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if any(c in _DIGITS for c in pw) and any(c in _LETTERS for c in pw):
            return pw


def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError, TypeError):
        return None
