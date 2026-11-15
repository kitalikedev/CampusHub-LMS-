"""Nhật ký thao tác (BR-AUD-01). Ghi trong cùng transaction; service gọi không commit."""
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.modules.audit.models import AuditLog
from src.modules.users.models import User


class AuditAction:
    USER_CREATED = "USER_CREATED"
    USERS_IMPORTED = "USERS_IMPORTED"
    USER_UPDATED = "USER_UPDATED"
    PASSWORD_RESET = "PASSWORD_RESET"
    ENROLLMENT_ADDED_BY_ADMIN = "ENROLLMENT_ADDED_BY_ADMIN"
    ENROLLMENT_DROPPED_BY_ADMIN = "ENROLLMENT_DROPPED_BY_ADMIN"
    GRADE_CHANGED = "GRADE_CHANGED"
    GRADES_PUBLISHED = "GRADES_PUBLISHED"
    SECTION_LOCKED = "SECTION_LOCKED"
    SECTION_UNLOCKED = "SECTION_UNLOCKED"
    REGRADE_RESOLVED = "REGRADE_RESOLVED"


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def log(db: Session, actor: Optional[User], action: str, entity_type: str, entity_id: int,
        before: Optional[Dict[str, Any]] = None, after: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None) -> None:
    db.add(AuditLog(actor_id=actor.id if actor else None, action=action, entity_type=entity_type,
                    entity_id=entity_id, before_data=_jsonable(before), after_data=_jsonable(after),
                    reason=reason))


def search(db: Session, action: Optional[str], entity_type: Optional[str], actor_id: Optional[int],
           page: int, page_size: int) -> Tuple[List[AuditLog], int]:
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()) \
        .offset((page - 1) * page_size).limit(page_size).all()
    return items, total
