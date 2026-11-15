"""Bài tập / cột điểm (BR-ASG-01…08)."""
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.permissions import ensure_not_locked, ensure_section_instructor, ensure_section_member
from src.core.time import to_naive_utc, utcnow
from src.domain.submission_policy import is_late
from src.modules.assignments.models import Assignment, GradeVisibility, SubmissionMode
from src.modules.assignments.schemas import AssignmentIn, AssignmentUpdate
from src.modules.grading.models import Grade
from src.modules.notifications import service as notifications
from src.modules.notifications.service import NotificationType
from src.modules.sections import service as sections
from src.modules.sections.models import CourseSection
from src.modules.submissions.models import Submission
from src.modules.users.models import User


def weight_total(db: Session, section_id: int, exclude_id: Optional[int] = None) -> Decimal:
    query = db.query(func.coalesce(func.sum(Assignment.weight_percent), 0)).filter(Assignment.section_id == section_id)
    if exclude_id is not None:
        query = query.filter(Assignment.id != exclude_id)
    return Decimal(str(query.scalar() or 0))


def _normalize(values: Dict[str, Any]) -> Dict[str, Any]:
    """BR-ASG-04, 05: OFFLINE không có hạn/chính sách trễ; MULTIPLE bắt buộc số lần."""
    mode = values["submission_mode"]
    if mode == SubmissionMode.OFFLINE:
        if values.get("due_at") is not None or values.get("late_policy") is not None:
            raise AppError("VALIDATION_ERROR", {"reason": "OFFLINE_HAS_DEADLINE"})
        values["due_at"], values["late_policy"] = None, None
    elif values.get("due_at") is None or values.get("late_policy") is None:
        raise AppError("VALIDATION_ERROR", {"reason": "DEADLINE_REQUIRED"})
    if mode == SubmissionMode.MULTIPLE:
        if not values.get("max_attempts"):
            raise AppError("VALIDATION_ERROR", {"reason": "MAX_ATTEMPTS_REQUIRED"})
    else:
        values["max_attempts"] = None
    values["due_at"] = to_naive_utc(values.get("due_at"))
    return values


def _check_weight(db: Session, section_id: int, weight: Decimal, exclude_id: Optional[int] = None) -> None:
    current = weight_total(db, section_id, exclude_id)
    if current + weight > Decimal(100):
        raise AppError("ASSIGNMENT_WEIGHT_EXCEEDED", {"current_total": float(current), "adding": float(weight)})


def get_assignment(db: Session, assignment_id: int) -> Assignment:
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise AppError("NOT_FOUND")
    return assignment


def section_of(db: Session, assignment: Assignment) -> CourseSection:
    return sections.get_section(db, assignment.section_id)


def list_for_section(db: Session, user: User, section_id: int) -> List[Assignment]:
    section = sections.get_section(db, section_id)
    ensure_section_member(db, section, user)
    return db.query(Assignment).filter(Assignment.section_id == section_id) \
        .order_by(Assignment.due_at.is_(None), Assignment.due_at, Assignment.id).all()


def create(db: Session, user: User, section_id: int, data: AssignmentIn) -> Assignment:
    section = sections.get_section(db, section_id)
    ensure_section_instructor(section, user)  # BR-ASG-03
    ensure_not_locked(section)
    values = _normalize(data.model_dump())
    _check_weight(db, section.id, values["weight_percent"])
    assignment = Assignment(section_id=section.id, created_by=user.id, **values)
    db.add(assignment)
    db.flush()
    notifications.notify(db, sections.enrolled_student_ids(db, section.id), NotificationType.ASSIGNMENT_CREATED,
                         {"title": assignment.title, "section_code": section.section_code},
                         f"/student/assignments/{assignment.id}")
    db.commit()
    return assignment


def has_submissions(db: Session, assignment_id: int) -> bool:
    return db.query(Submission.id).filter(Submission.assignment_id == assignment_id).first() is not None


def has_grades(db: Session, assignment_id: int) -> bool:
    return db.query(Grade.id).filter(Grade.assignment_id == assignment_id).first() is not None


def update(db: Session, user: User, assignment_id: int, data: AssignmentUpdate) -> Assignment:
    assignment = get_assignment(db, assignment_id)
    section = section_of(db, assignment)
    ensure_section_instructor(section, user)
    ensure_not_locked(section)
    changes = data.model_dump(exclude_unset=True)
    merged = {k: getattr(assignment, k) for k in ("submission_mode", "max_attempts", "due_at", "late_policy")}
    merged.update({k: v for k, v in changes.items() if k in merged})
    submitted = has_submissions(db, assignment.id)
    if submitted and (merged["submission_mode"] != assignment.submission_mode
                      or merged["late_policy"] != assignment.late_policy):
        raise AppError("ASSIGNMENT_HAS_SUBMISSIONS")  # BR-ASG-06
    merged = _normalize(merged)
    if "weight_percent" in changes and changes["weight_percent"] is not None:
        _check_weight(db, section.id, changes["weight_percent"], exclude_id=assignment.id)
        assignment.weight_percent = changes["weight_percent"]
    for field in ("title", "description"):
        if field in changes and (changes[field] is not None or field == "description"):
            setattr(assignment, field, changes[field])
    due_changed = merged["due_at"] != assignment.due_at
    for field, value in merged.items():
        setattr(assignment, field, value)
    if due_changed:  # BR-ASG-06: tính lại nhãn trễ theo hạn mới
        for sub in db.query(Submission).filter(Submission.assignment_id == assignment.id):
            sub.is_late = is_late(sub.submitted_at, assignment.due_at)
    new_visibility = changes.get("grade_visibility")
    if new_visibility and new_visibility != assignment.grade_visibility:
        if new_visibility == GradeVisibility.MANUAL and has_grades(db, assignment.id):
            raise AppError("VALIDATION_ERROR", {"reason": "GRADES_ALREADY_VISIBLE"})
        assignment.grade_visibility = new_visibility
        if new_visibility == GradeVisibility.IMMEDIATE:
            from src.modules.grading.service import reveal_grades  # tránh import vòng
            reveal_grades(db, assignment, section)
    db.commit()
    return assignment


def delete(db: Session, user: User, assignment_id: int) -> None:
    assignment = get_assignment(db, assignment_id)
    section = section_of(db, assignment)
    ensure_section_instructor(section, user)
    ensure_not_locked(section)
    if has_submissions(db, assignment.id) or has_grades(db, assignment.id):
        raise AppError("ASSIGNMENT_HAS_SUBMISSIONS")  # BR-ASG-07
    db.delete(assignment)
    db.commit()


def touch_published(assignment: Assignment) -> None:
    assignment.grades_published_at = assignment.grades_published_at or utcnow()
