"""Truy vấn lớp học phần và lịch. Không commit (ADR-05)."""
from typing import Dict, Iterable, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.modules.enrollments.models import Enrollment, EnrollmentStatus
from src.modules.sections.models import CourseSection, ScheduleSlot


def get(db: Session, section_id: int, for_update: bool = False) -> Optional[CourseSection]:
    query = db.query(CourseSection).filter(CourseSection.id == section_id)
    if for_update:
        query = query.with_for_update()  # BR-ENR-03: khóa dòng lớp khi đăng ký
    return query.first()


def enrolled_counts(db: Session, section_ids: Iterable[int]) -> Dict[int, int]:
    ids = list(section_ids)
    if not ids:
        return {}
    rows = db.query(Enrollment.section_id, func.count(Enrollment.id)).filter(
        Enrollment.section_id.in_(ids), Enrollment.status == EnrollmentStatus.ENROLLED
    ).group_by(Enrollment.section_id).all()
    return {sid: count for sid, count in rows}


def slots_in_semester(db: Session, semester_id: int, exclude_section_id: Optional[int] = None) -> List[ScheduleSlot]:
    query = db.query(ScheduleSlot).join(CourseSection, CourseSection.id == ScheduleSlot.section_id) \
        .filter(CourseSection.semester_id == semester_id)
    if exclude_section_id is not None:
        query = query.filter(CourseSection.id != exclude_section_id)
    return query.all()
