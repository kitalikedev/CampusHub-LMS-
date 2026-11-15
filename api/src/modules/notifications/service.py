"""Thông báo hệ thống (BR-NOT-01). Ghi trong cùng transaction với thao tác gốc; service gọi không commit."""
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.modules.notifications.models import Notification
from src.modules.users.models import User


class NotificationType:
    ASSIGNMENT_CREATED = "ASSIGNMENT_CREATED"
    GRADE_VISIBLE = "GRADE_VISIBLE"
    ANNOUNCEMENT_POSTED = "ANNOUNCEMENT_POSTED"
    ENROLLED_BY_ADMIN = "ENROLLED_BY_ADMIN"
    REGRADE_SUBMITTED = "REGRADE_SUBMITTED"
    REGRADE_RESOLVED = "REGRADE_RESOLVED"
    RESULT_FINALIZED = "RESULT_FINALIZED"


def notify(db: Session, user_ids: Iterable[int], type_: str, params: Dict[str, Any],
           link: Optional[str] = None) -> None:
    for uid in sorted(set(user_ids)):
        db.add(Notification(user_id=uid, type=type_, params=params, link=link))


def list_for(db: Session, user: User, unread_only: bool, limit: int = 50) -> Tuple[List[Notification], int]:
    query = db.query(Notification).filter(Notification.user_id == user.id)
    unread = query.filter(Notification.is_read.is_(False)).count()
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    items = query.order_by(Notification.created_at.desc(), Notification.id.desc()).limit(limit).all()
    return items, unread


def mark_read(db: Session, user: User, notification_id: int) -> None:
    item = db.get(Notification, notification_id)
    if item is None or item.user_id != user.id:
        raise AppError("NOT_FOUND")
    item.is_read = True
    db.commit()


def mark_all_read(db: Session, user: User) -> None:
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False)) \
        .update({Notification.is_read: True}, synchronize_session=False)
    db.commit()
