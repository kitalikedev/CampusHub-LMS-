from typing import Any, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.core.schemas import Num, ORMModel
from src.core.time import UTCDateTime
from src.modules.regrades import service
from src.modules.users.models import Role, User
from src.modules.users.schemas import UserBrief

router = APIRouter(tags=["regrades"])


class RegradeCreate(BaseModel):
    reason: str = ""


class RegradeResolve(BaseModel):
    accept: bool
    new_score: Optional[Any] = None
    response: Optional[str] = None


class RegradeRequestOut(ORMModel):
    id: int
    grade_id: int
    reason: str
    status: str
    old_score: Num
    new_score: Optional[Num]
    response: Optional[str]
    created_at: UTCDateTime
    resolved_at: Optional[UTCDateTime]


class RegradeView(BaseModel):
    request: RegradeRequestOut
    assignment_id: int
    assignment_title: str
    section_id: int
    section_code: str
    subject_name: str
    student: UserBrief
    current_score: Num


@router.post("/grades/{grade_id}/regrade-requests", response_model=RegradeView, status_code=201)
def create(grade_id: int, data: RegradeCreate, db: Session = Depends(get_db),
           user: User = Depends(require_roles(Role.STUDENT))):
    return service.describe(db, service.create(db, user, grade_id, data.reason))


@router.get("/regrade-requests", response_model=List[RegradeView])
def list_requests(status: Optional[str] = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_for(db, user, status)


@router.post("/regrade-requests/{request_id}/resolve", response_model=RegradeView)
def resolve(request_id: int, data: RegradeResolve, db: Session = Depends(get_db),
            user: User = Depends(require_roles(Role.INSTRUCTOR))):
    return service.describe(db, service.resolve(db, user, request_id, data.accept, data.new_score, data.response))
