from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.core.errors import AppError
from src.core.schemas import Num, ORMModel
from src.core.time import UTCDateTime
from src.modules.assignments import service as assignments
from src.modules.enrollments import service as enrollments
from src.modules.grading.models import Grade
from src.modules.sections import service as sections
from src.modules.submissions import service
from src.modules.users.models import Role, User
from src.modules.users.schemas import UserBrief

router = APIRouter(tags=["submissions"])


class FileOut(ORMModel):
    id: int
    original_name: str
    size_bytes: int


class SubmissionOut(ORMModel):
    id: int
    assignment_id: int
    student_id: int
    attempt_no: int
    content_url: Optional[str]
    file: Optional[FileOut]
    is_late: bool
    submitted_at: UTCDateTime


class GradeBrief(ORMModel):
    id: int
    score: Num
    feedback: Optional[str]
    visible_at: Optional[UTCDateTime]
    updated_at: UTCDateTime


class SubmissionRow(BaseModel):
    student: UserBrief
    latest: Optional[SubmissionOut]
    attempts_count: int
    grade: Optional[GradeBrief]


@router.post("/assignments/{assignment_id}/submissions", response_model=SubmissionOut, status_code=201)
def submit(assignment_id: int, content_url: Optional[str] = Form(default=None),
           file: Optional[UploadFile] = File(default=None), db: Session = Depends(get_db),
           user: User = Depends(require_roles(Role.STUDENT))):
    return service.submit(db, user, assignment_id, content_url, file)


@router.get("/assignments/{assignment_id}/submissions/mine", response_model=List[SubmissionOut])
def my_submissions(assignment_id: int, db: Session = Depends(get_db),
                   user: User = Depends(require_roles(Role.STUDENT))):
    return service.my_attempts(db, user, assignment_id)


@router.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionRow])
def list_submissions(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Mọi SV của lớp kèm lần nộp mới nhất và điểm (FR-SUB-04, FR-GRD-01)."""
    assignment = assignments.get_assignment(db, assignment_id)
    section = assignments.section_of(db, assignment)
    if user.role == Role.STUDENT:
        raise AppError("FORBIDDEN")
    sections.ensure_can_view(db, section, user)
    latest = service.latest_by_student(db, assignment.id)
    grades = {g.student_id: g for g in db.query(Grade).filter(Grade.assignment_id == assignment.id)}
    rows = []
    for enrollment in enrollments.section_roster(db, section.id):
        sid = enrollment.student_id
        sub, count = latest.get(sid, (None, 0))
        grade = grades.get(sid)
        rows.append(SubmissionRow(student=UserBrief.model_validate(enrollment.student),
                                  latest=SubmissionOut.model_validate(sub) if sub else None, attempts_count=count,
                                  grade=GradeBrief.model_validate(grade) if grade else None))
    return rows


@router.get("/files/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    path, stored = service.file_for_download(db, user, file_id)
    return FileResponse(path, media_type=stored.mime_type, filename=stored.original_name)
