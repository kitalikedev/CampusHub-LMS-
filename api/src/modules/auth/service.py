from typing import Tuple

from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.security import create_access_token, hash_password, password_length_ok, verify_password
from src.core.time import utcnow
from src.modules.users import repository as users_repo
from src.modules.users.models import User


def login(db: Session, email: str, password: str) -> Tuple[str, User]:
    user = users_repo.get_by_email(db, email)
    # Cùng một lỗi cho sai email và sai mật khẩu (AC-AUTH-01.2).
    if user is None or not verify_password(password, user.password_hash):
        raise AppError("AUTH_INVALID_CREDENTIALS")
    if not user.is_active:
        raise AppError("ACCOUNT_DISABLED")
    user.last_login_at = utcnow()
    db.commit()
    return create_access_token(user.id, user.role), user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.password_hash):
        raise AppError("CURRENT_PASSWORD_INCORRECT", {"field": "current_password"})
    if not password_length_ok(new_password):
        raise AppError("PASSWORD_POLICY_VIOLATION", {"reason": "LENGTH", "min_bytes": 8, "max_bytes": 72})
    if verify_password(new_password, user.password_hash):
        raise AppError("PASSWORD_POLICY_VIOLATION", {"reason": "SAME_AS_CURRENT"})
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.commit()
