"""Truy vấn người dùng. Không commit (ADR-05)."""
from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.modules.users.models import Role, User


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == normalize_email(email)).first()


def get_by_student_code(db: Session, code: str) -> Optional[User]:
    return db.query(User).filter(User.student_code == code).first()


def search(db: Session, q: Optional[str], role: Optional[str], page: int, page_size: int) -> Tuple[List[User], int]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(User.email.ilike(like), User.full_name.ilike(like), User.student_code.ilike(like)))
    total = query.count()
    items = query.order_by(User.role, User.full_name).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def count_active_admins(db: Session) -> int:
    return db.query(User).filter(User.role == Role.ADMIN, User.is_active.is_(True)).count()


def add(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user
