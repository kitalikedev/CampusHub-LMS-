"""Lấy người dùng hiện tại từ JWT (06 §2.6)."""
from typing import Callable, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.errors import AppError
from src.core.security import decode_access_token
from src.modules.users.models import User

_bearer = HTTPBearer(auto_error=False)


def _load_user(creds: Optional[HTTPAuthorizationCredentials], db: Session) -> User:
    if creds is None or not creds.credentials:
        raise AppError("AUTH_REQUIRED")
    user_id = decode_access_token(creds.credentials)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise AppError("AUTH_REQUIRED")
    if not user.is_active:
        raise AppError("ACCOUNT_DISABLED")  # BR-ACC-06: chặn ngay ở request kế tiếp
    return user


def get_current_user_allow_password_change(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer), db: Session = Depends(get_db)
) -> User:
    """Dùng cho /me, /auth/change-password: cho phép khi đang phải đổi mật khẩu."""
    return _load_user(creds, db)


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer), db: Session = Depends(get_db)
) -> User:
    user = _load_user(creds, db)
    if user.must_change_password:
        raise AppError("PASSWORD_CHANGE_REQUIRED")  # BR-ACC-04
    return user


def require_roles(*roles: str) -> Callable[..., User]:
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise AppError("FORBIDDEN")
        return user

    return _checker
