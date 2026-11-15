from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.core.schemas import Num, ORMModel
from src.core.time import UTCDateTime
from src.modules.assignments.schemas import AssignmentOut
from src.modules.grading import service
from src.modules.sections import service as sections
from src.modules.sections.schemas import SectionOut
from src.modules.submissions.router import GradeBrief, SubmissionOut
from src.modules.users.models import Role, User
from src.modules.users.schemas import UserBrief

router = APIRouter(tags=["grading"])


class GradeIn(BaseModel):
    score: Any
    feedback: Optional[str] = None


class GradeOut(ORMModel):
    id: int
    assignment_id: int
    student_id: int
    score: Num
    feedback: Optional[str]
    visible_at: Optional[UTCDateTime]
    updated_at: UTCDateTime


class ResultOut(ORMModel):
    final_score_10: Num
    letter_grade: Optional[str]
    grade_point: Optional[Num]
    is_passed: bool
    finalized_at: UTCDateTime


class GradebookRow(BaseModel):
    student: UserBrief
    scores: Dict[int, Optional[Num]]
    provisional_score: Optional[Num]
    graded_weight: Num
    result: Optional[ResultOut]


class Gradebook(BaseModel):
    section_id: int
    status: str
    assignments: List[AssignmentOut]
    weight_total: Num
    rows: List[GradebookRow]


class RegradeBrief(ORMModel):
    id: int
    status: str
    new_score: Optional[Num]
    response: Optional[str]


class MyGradeItem(BaseModel):
    assignment: AssignmentOut
    status: str
    visible: bool
    grade_hidden: bool
    attempts_count: int
    latest: Optional[SubmissionOut]
    grade: Optional[GradeBrief]
    regrade: Optional[RegradeBrief]


class MyGrades(BaseModel):
    section_id: int
    status: str
    items: List[MyGradeItem]
    provisional_score: Optional[Num]
    graded_weight: Num
    result: Optional[ResultOut]


class LockCheck(BaseModel):
    can_lock: bool
    checks: List[Dict[str, Any]]


class UnlockRequest(BaseModel):
    reason: str = ""


@router.put("/assignments/{assignment_id}/grades/{student_id}", response_model=GradeOut)
def put_grade(assignment_id: int, student_id: int, data: GradeIn, db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    return service.put_grade(db, user, assignment_id, student_id, data.score, data.feedback)


@router.post("/assignments/{assignment_id}/publish-grades", response_model=AssignmentOut)
def publish_grades(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.publish_grades(db, user, assignment_id)


@router.get("/sections/{section_id}/gradebook", response_model=Gradebook)
def gradebook(section_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.gradebook(db, user, section_id)


@router.get("/sections/{section_id}/gradebook.csv")
def gradebook_csv(section_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    filename, content = service.gradebook_csv(db, user, section_id)
    return Response(content=content.encode("utf-8"), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": 'attachment; filename="%s"' % filename})


@router.get("/sections/{section_id}/my-grades", response_model=MyGrades)
def my_grades(section_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.STUDENT))):
    return service.my_grades(db, user, section_id)


@router.get("/sections/{section_id}/lock-check", response_model=LockCheck)
def lock_check(section_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.lock_check(db, user, section_id)


@router.post("/sections/{section_id}/lock", response_model=SectionOut)
def lock(section_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    section = service.lock(db, user, section_id)
    return sections.section_out(db, section, user)


@router.post("/sections/{section_id}/unlock", response_model=SectionOut)
def unlock(section_id: int, data: UnlockRequest, db: Session = Depends(get_db),
           admin: User = Depends(require_roles(Role.ADMIN))):
    section = service.unlock(db, admin, section_id, data.reason)
    return sections.section_out(db, section, admin)
