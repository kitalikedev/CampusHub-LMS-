from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user
from src.core.schemas import Message, ORMModel
from src.core.time import UTCDateTime
from src.modules.notifications import service
from src.modules.users.models import User

router = APIRouter(prefix="/me/notifications", tags=["notifications"])


class NotificationOut(ORMModel):
    id: int
    type: str
    params: Dict[str, Any]
    link: Optional[str]
    is_read: bool
    created_at: UTCDateTime


class NotificationList(BaseModel):
    items: List[NotificationOut]
    unread_count: int


@router.get("", response_model=NotificationList)
def list_notifications(unread: bool = False, db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    items, unread_count = service.list_for(db, user, unread)
    return NotificationList(items=items, unread_count=unread_count)


@router.post("/{notification_id}/read", response_model=Message)
def read_one(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.mark_read(db, user, notification_id)
    return Message()


@router.post("/read-all", response_model=Message)
def read_all(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.mark_all_read(db, user)
    return Message()
