from typing import List, Optional

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.core.errors import AppError
from src.core.schemas import ORMModel
from src.core.time import UTCDateTime
from src.modules.enrollments import service
from src.modules.sections import service as sections
from src.modules.users.models import Role, User
from src.modules.users.schemas import UserBrief

router = APIRouter(tags=["enrollments"])


class EnrollmentOut(ORMModel):
    id: int
    section_id: int
    student_id: int
    status: str
    source: str
    override_reason: Optional[str]
    enrolled_at: UTCDateTime


class SelfEnrollResult(BaseModel):
    enrollment: EnrollmentOut
    warnings: List[str]


class RosterRow(BaseModel):
    enrollment_id: int
    source: str
    enrolled_at: UTCDateTime
    student: UserBrief


class AdminEnrollRequest(BaseModel):
    student_id: int
    override_reason: Optional[str] = None


@router.post("/sections/{section_id}/enrollments/self", response_model=SelfEnrollResult, status_code=201)
def self_enroll(section_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.STUDENT))):
    enrollment, warnings = service.self_enroll(db, user, section_id)
    return SelfEnrollResult(enrollment=EnrollmentOut.model_validate(enrollment), warnings=warnings)


@router.delete("/sections/{section_id}/enrollments/self", status_code=204)
def self_drop(section_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.STUDENT))):
    service.self_drop(db, user, section_id)
    return Response(status_code=204)


@router.get("/sections/{section_id}/enrollments", response_model=List[RosterRow])
def roster(section_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    section = sections.get_section(db, section_id)
    if user.role == Role.STUDENT:
        raise AppError("FORBIDDEN")
    sections.ensure_can_view(db, section, user)
    return [RosterRow(enrollment_id=e.id, source=e.source, enrolled_at=e.enrolled_at,
                      student=UserBrief.model_validate(e.student)) for e in service.section_roster(db, section_id)]


@router.post("/sections/{section_id}/enrollments", response_model=EnrollmentOut, status_code=201)
def admin_enroll(section_id: int, data: AdminEnrollRequest, db: Session = Depends(get_db),
                 admin: User = Depends(require_roles(Role.ADMIN))):
    return service.admin_enroll(db, admin, section_id, data.student_id, data.override_reason)


@router.delete("/sections/{section_id}/enrollments/{student_id}", status_code=204)
def admin_drop(section_id: int, student_id: int, db: Session = Depends(get_db),
               admin: User = Depends(require_roles(Role.ADMIN))):
    service.admin_drop(db, admin, section_id, student_id)
    return Response(status_code=204)
