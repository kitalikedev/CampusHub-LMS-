from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import require_roles
from src.core.schemas import ORMModel, Page
from src.core.time import UTCDateTime
from src.modules.audit import service
from src.modules.users.models import Role, User

router = APIRouter(prefix="/admin/audit-logs", tags=["audit"])


class AuditLogOut(ORMModel):
    id: int
    actor_id: Optional[int]
    action: str
    entity_type: str
    entity_id: int
    before_data: Optional[Any]
    after_data: Optional[Any]
    reason: Optional[str]
    created_at: UTCDateTime


@router.get("", response_model=Page[AuditLogOut])
def list_logs(action: Optional[str] = None, entity_type: Optional[str] = None, actor_id: Optional[int] = None,
              page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
              db: Session = Depends(get_db), _admin: User = Depends(require_roles(Role.ADMIN))):
    items, total = service.search(db, action, entity_type, actor_id, page, page_size)
    return Page[AuditLogOut](items=items, total=total)
