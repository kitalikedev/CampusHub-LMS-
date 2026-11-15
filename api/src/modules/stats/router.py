"""Thống kê cho Admin (FR-STA-01, mức Could)."""
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import require_roles
from src.modules.academics.models import Subject
from src.modules.enrollments.models import CourseResult, Enrollment
from src.modules.sections.models import CourseSection
from src.modules.users.models import Role, User

router = APIRouter(prefix="/admin/stats", tags=["stats"])


class SubjectPassRate(BaseModel):
    subject_code: str
    subject_name: str
    finalized: int
    passed: int


class Stats(BaseModel):
    users_by_role: Dict[str, int]
    sections_by_status: Dict[str, int]
    letter_distribution: Dict[str, int]
    pass_rates: List[SubjectPassRate]


@router.get("", response_model=Stats)
def stats(semester_id: Optional[int] = None, db: Session = Depends(get_db),
          _admin: User = Depends(require_roles(Role.ADMIN))):
    users = dict(db.query(User.role, func.count(User.id)).filter(User.is_active.is_(True)).group_by(User.role).all())
    section_q = db.query(CourseSection.status, func.count(CourseSection.id))
    result_q = db.query(CourseResult).join(Enrollment, Enrollment.id == CourseResult.enrollment_id) \
        .join(CourseSection, CourseSection.id == Enrollment.section_id)
    if semester_id:
        section_q = section_q.filter(CourseSection.semester_id == semester_id)
        result_q = result_q.filter(CourseSection.semester_id == semester_id)
    letters: Dict[str, int] = {}
    rates: Dict[int, Dict[str, int]] = {}
    for result in result_q.all():
        if result.letter_grade:
            letters[result.letter_grade] = letters.get(result.letter_grade, 0) + 1
        subject_id = result.enrollment and db.get(CourseSection, result.enrollment.section_id).subject_id
        bucket = rates.setdefault(subject_id, {"finalized": 0, "passed": 0})
        bucket["finalized"] += 1
        bucket["passed"] += 1 if result.is_passed else 0
    pass_rates = []
    for subject_id, bucket in rates.items():
        subject = db.get(Subject, subject_id)
        pass_rates.append(SubjectPassRate(subject_code=subject.code, subject_name=subject.name, **bucket))
    return Stats(users_by_role=users, sections_by_status=dict(section_q.group_by(CourseSection.status).all()),
                 letter_distribution=letters, pass_rates=sorted(pass_rates, key=lambda r: r.subject_code))
