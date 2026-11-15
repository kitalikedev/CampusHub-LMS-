"""Phúc khảo (BR-REG-01…04)."""
from datetime import timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.errors import AppError
from src.core.permissions import ensure_not_locked, ensure_section_instructor
from src.core.time import utcnow
from src.modules.assignments.models import Assignment
from src.modules.audit import service as audit
from src.modules.audit.service import AuditAction
from src.modules.grading.models import Grade
from src.modules.grading.service import parse_score
from src.modules.notifications import service as notifications
from src.modules.notifications.service import NotificationType
from src.modules.regrades.models import RegradeRequest, RegradeStatus
from src.modules.sections import service as sections
from src.modules.sections.models import CourseSection
from src.modules.users.models import Role, User


def _context(db: Session, grade: Grade):
    assignment = db.get(Assignment, grade.assignment_id)
    return assignment, sections.get_section(db, assignment.section_id)


def create(db: Session, student: User, grade_id: int, reason: str) -> RegradeRequest:
    grade = db.get(Grade, grade_id)
    if grade is None or grade.student_id != student.id or grade.visible_at is None:
        raise AppError("NOT_FOUND")  # chỉ phúc khảo điểm đang hiện với mình
    assignment, section = _context(db, grade)
    ensure_not_locked(section)
    if utcnow() > grade.visible_at + timedelta(days=settings.REGRADE_WINDOW_DAYS):
        raise AppError("REGRADE_WINDOW_CLOSED", {"days": settings.REGRADE_WINDOW_DAYS})
    reason = (reason or "").strip()
    if not reason:
        raise AppError("REGRADE_REASON_REQUIRED")
    if db.query(RegradeRequest.id).filter(RegradeRequest.grade_id == grade.id).first():
        raise AppError("REGRADE_EXISTS")  # BR-REG-02
    request = RegradeRequest(grade_id=grade.id, reason=reason, old_score=grade.score)
    db.add(request)
    notifications.notify(db, [section.instructor_id], NotificationType.REGRADE_SUBMITTED,
                         {"title": assignment.title, "student_name": student.full_name,
                          "section_code": section.section_code}, "/instructor/regrades")
    db.commit()
    return request


def describe(db: Session, request: RegradeRequest) -> Dict[str, Any]:
    grade = db.get(Grade, request.grade_id)
    assignment, section = _context(db, grade)
    return {"request": request, "assignment_id": assignment.id, "assignment_title": assignment.title,
            "section_id": section.id, "section_code": section.section_code,
            "subject_name": section.subject.name, "student": db.get(User, grade.student_id),
            "current_score": grade.score}


def list_for(db: Session, user: User, status: Optional[str]) -> List[Dict[str, Any]]:
    query = db.query(RegradeRequest).join(Grade, Grade.id == RegradeRequest.grade_id) \
        .join(Assignment, Assignment.id == Grade.assignment_id) \
        .join(CourseSection, CourseSection.id == Assignment.section_id)
    if user.role == Role.STUDENT:
        query = query.filter(Grade.student_id == user.id)
    elif user.role == Role.INSTRUCTOR:
        query = query.filter(CourseSection.instructor_id == user.id)
    if status:
        query = query.filter(RegradeRequest.status == status)
    return [describe(db, r) for r in query.order_by(RegradeRequest.created_at.desc()).all()]


def resolve(db: Session, instructor: User, request_id: int, accept: bool, new_score: Any,
            response: Optional[str]) -> RegradeRequest:
    request = db.get(RegradeRequest, request_id)
    if request is None:
        raise AppError("NOT_FOUND")
    grade = db.get(Grade, request.grade_id)
    assignment, section = _context(db, grade)
    ensure_section_instructor(section, instructor)
    ensure_not_locked(section)
    if request.status != RegradeStatus.PENDING:
        raise AppError("INVALID_STATE_TRANSITION", {"from": request.status})
    response = (response or "").strip() or None
    if accept:
        score = parse_score(new_score)
        if score != grade.score:
            audit.log(db, instructor, AuditAction.GRADE_CHANGED, "grade", grade.id,
                      before={"score": grade.score}, after={"score": score}, reason="REGRADE")
        grade.score, grade.graded_by = score, instructor.id
        request.status, request.new_score = RegradeStatus.ACCEPTED, score
    else:
        if not response:
            raise AppError("REGRADE_REASON_REQUIRED")  # BR-REG-03
        request.status = RegradeStatus.REJECTED
    request.response, request.resolved_by, request.resolved_at = response, instructor.id, utcnow()
    audit.log(db, instructor, AuditAction.REGRADE_RESOLVED, "regrade_request", request.id,
              before={"score": request.old_score}, after={"status": request.status, "score": grade.score})
    notifications.notify(db, [grade.student_id], NotificationType.REGRADE_RESOLVED,
                         {"title": assignment.title, "status": request.status},
                         f"/student/assignments/{assignment.id}")
    db.commit()
    return request
