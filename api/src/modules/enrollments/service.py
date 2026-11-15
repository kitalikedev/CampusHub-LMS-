"""Đăng ký học (BR-ENR-01…09). Thứ tự kiểm tra theo 03 §3."""
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.permissions import ensure_not_locked
from src.core.time import utcnow
from src.domain.schedule import Slot, overlaps
from src.modules.academics import service as academics
from src.modules.academics.models import Subject
from src.modules.audit import service as audit
from src.modules.audit.service import AuditAction
from src.modules.enrollments.models import CourseResult, Enrollment, EnrollmentSource, EnrollmentStatus
from src.modules.notifications import service as notifications
from src.modules.notifications.service import NotificationType
from src.modules.sections import repository as sections_repo
from src.modules.sections.models import CourseSection, SectionStatus
from src.modules.users.models import Role, User

Violation = Dict[str, Any]


def _active_sections(db: Session, student_id: int, semester_id: int, exclude_id: int) -> List[CourseSection]:
    return db.query(CourseSection).join(Enrollment, Enrollment.section_id == CourseSection.id).filter(
        Enrollment.student_id == student_id, Enrollment.status == EnrollmentStatus.ENROLLED,
        CourseSection.semester_id == semester_id, CourseSection.id != exclude_id,
    ).all()


def _passed_subject_ids(db: Session, student_id: int) -> set:
    rows = db.query(CourseSection.subject_id).join(Enrollment, Enrollment.section_id == CourseSection.id) \
        .join(CourseResult, CourseResult.enrollment_id == Enrollment.id) \
        .filter(Enrollment.student_id == student_id, CourseResult.is_passed.is_(True)).all()
    return {r[0] for r in rows}


def _has_result_for_subject(db: Session, student_id: int, subject_id: int) -> bool:
    return db.query(CourseResult.enrollment_id).join(Enrollment, Enrollment.id == CourseResult.enrollment_id) \
        .join(CourseSection, CourseSection.id == Enrollment.section_id) \
        .filter(Enrollment.student_id == student_id, CourseSection.subject_id == subject_id).first() is not None


def check_rules(db: Session, section: CourseSection, student: User) -> List[Violation]:
    """Kiểm tra BR-ENR-03…07, trả mọi vi phạm theo đúng thứ tự (03 §3)."""
    violations: List[Violation] = []
    current = _active_sections(db, student.id, section.semester_id, section.id)
    # BR-ENR-07: cùng môn trong kỳ, hoặc đã có kết quả môn đó.
    same = next((s for s in current if s.subject_id == section.subject_id), None)
    if same or _has_result_for_subject(db, student.id, section.subject_id):
        violations.append({"code": "SUBJECT_ALREADY_TAKEN",
                           "params": {"subject_code": section.subject.code,
                                      "section_code": same.section_code if same else None}})
    # BR-ENR-03: sĩ số.
    enrolled = sections_repo.enrolled_counts(db, [section.id]).get(section.id, 0)
    if enrolled >= section.capacity:
        violations.append({"code": "SECTION_FULL", "params": {"capacity": section.capacity}})
    # BR-ENR-04: trùng lịch.
    for other in current:
        clash = next(((a, b) for a in section.slots for b in other.slots
                      if overlaps(Slot(a.day_of_week, a.start_time, a.end_time),
                                  Slot(b.day_of_week, b.start_time, b.end_time))), None)
        if clash:
            b = clash[1]
            violations.append({"code": "SCHEDULE_CONFLICT", "params": {
                "section_code": other.section_code, "subject_code": other.subject.code, "day": b.day_of_week,
                "start": b.start_time.strftime("%H:%M"), "end": b.end_time.strftime("%H:%M")}})
            break
    # BR-ENR-05: tiên quyết (đã khóa sổ và Đạt).
    required = academics.prerequisite_map(db).get(section.subject_id, set())
    missing = required - _passed_subject_ids(db, student.id)
    if missing:
        codes = [s.code for s in db.query(Subject).filter(Subject.id.in_(missing)).order_by(Subject.code)]
        violations.append({"code": "PREREQUISITE_NOT_MET", "params": {"missing": codes}})
    # BR-ENR-06: giới hạn tín chỉ.
    credits = sum(s.subject.credits for s in current)
    if credits + section.subject.credits > section.semester.max_credits:
        violations.append({"code": "CREDIT_LIMIT_EXCEEDED", "params": {
            "current": credits, "adding": section.subject.credits, "max": section.semester.max_credits}})
    return violations


def _upsert(db: Session, section: CourseSection, student: User, source: str,
            reason: Optional[str]) -> Enrollment:
    existing = db.query(Enrollment).filter(Enrollment.section_id == section.id,
                                           Enrollment.student_id == student.id).first()
    if existing and existing.status == EnrollmentStatus.ENROLLED:
        raise AppError("ALREADY_ENROLLED")
    if existing:  # BR-ENR-09: đăng ký lại dùng bản ghi cũ
        existing.status, existing.source, existing.override_reason = EnrollmentStatus.ENROLLED, source, reason
        existing.enrolled_at, existing.dropped_at = utcnow(), None
        return existing
    enrollment = Enrollment(section_id=section.id, student_id=student.id, status=EnrollmentStatus.ENROLLED,
                            source=source, override_reason=reason)
    db.add(enrollment)
    return enrollment


def _credit_warnings(db: Session, section: CourseSection, student: User) -> List[str]:
    total = sum(s.subject.credits for s in _active_sections(db, student.id, section.semester_id, 0))
    return ["BELOW_MIN_CREDITS"] if total < section.semester.min_credits else []


def self_enroll(db: Session, student: User, section_id: int) -> Tuple[Enrollment, List[str]]:
    try:
        section = sections_repo.get(db, section_id, for_update=True)
        if section is None:
            raise AppError("NOT_FOUND")
        if not academics.is_registration_open(section.semester):
            raise AppError("ENROLL_PERIOD_CLOSED")  # BR-ENR-01
        if section.status != SectionStatus.PUBLISHED:
            raise AppError("SECTION_NOT_OPEN")
        existing = db.query(Enrollment).filter(Enrollment.section_id == section.id,
                                               Enrollment.student_id == student.id,
                                               Enrollment.status == EnrollmentStatus.ENROLLED).first()
        if existing:
            raise AppError("ALREADY_ENROLLED")
        violations = check_rules(db, section, student)
        if violations:
            first = violations[0]
            raise AppError(first["code"], first["params"])
        enrollment = _upsert(db, section, student, EnrollmentSource.SELF, None)
        db.flush()
        warnings = _credit_warnings(db, section, student)
        db.commit()
        return enrollment, warnings
    except Exception:
        db.rollback()
        raise


def self_drop(db: Session, student: User, section_id: int) -> None:
    section = sections_repo.get(db, section_id)
    if section is None:
        raise AppError("NOT_FOUND")
    ensure_not_locked(section)
    if not academics.is_registration_open(section.semester):
        raise AppError("ENROLL_PERIOD_CLOSED")  # BR-ENR-02
    enrollment = db.query(Enrollment).filter(Enrollment.section_id == section.id,
                                             Enrollment.student_id == student.id,
                                             Enrollment.status == EnrollmentStatus.ENROLLED).first()
    if enrollment is None:
        raise AppError("NOT_ENROLLED")
    enrollment.status, enrollment.dropped_at = EnrollmentStatus.DROPPED, utcnow()
    db.commit()


def admin_enroll(db: Session, admin: User, section_id: int, student_id: int,
                 override_reason: Optional[str]) -> Enrollment:
    """Admin xếp SV; vi phạm thì liệt kê đủ và chỉ vượt khi có lý do (BR-ENR-08)."""
    try:
        section = sections_repo.get(db, section_id, for_update=True)
        if section is None:
            raise AppError("NOT_FOUND")
        ensure_not_locked(section)
        student = db.get(User, student_id)
        if student is None or student.role != Role.STUDENT or not student.is_active:
            raise AppError("VALIDATION_ERROR", {"field": "student_id", "reason": "NOT_ACTIVE_STUDENT"})
        violations = check_rules(db, section, student)
        reason = (override_reason or "").strip() or None
        if violations and not reason:
            raise AppError("ENROLLMENT_RULES_VIOLATED", {"violations": violations})
        enrollment = _upsert(db, section, student, EnrollmentSource.ADMIN, reason)
        db.flush()
        audit.log(db, admin, AuditAction.ENROLLMENT_ADDED_BY_ADMIN, "enrollment", enrollment.id,
                  after={"section_id": section.id, "student_id": student.id,
                         "violations": [v["code"] for v in violations]}, reason=reason)
        notifications.notify(db, [student.id], NotificationType.ENROLLED_BY_ADMIN,
                             {"section_code": section.section_code, "subject_name": section.subject.name},
                             f"/student/classes/{section.id}")
        db.commit()
        return enrollment
    except Exception:
        db.rollback()
        raise


def admin_drop(db: Session, admin: User, section_id: int, student_id: int) -> None:
    section = sections_repo.get(db, section_id)
    if section is None:
        raise AppError("NOT_FOUND")
    ensure_not_locked(section)
    enrollment = db.query(Enrollment).filter(Enrollment.section_id == section_id, Enrollment.student_id == student_id,
                                             Enrollment.status == EnrollmentStatus.ENROLLED).first()
    if enrollment is None:
        raise AppError("NOT_ENROLLED")
    enrollment.status, enrollment.dropped_at = EnrollmentStatus.DROPPED, utcnow()
    audit.log(db, admin, AuditAction.ENROLLMENT_DROPPED_BY_ADMIN, "enrollment", enrollment.id,
              before={"section_id": section_id, "student_id": student_id})
    db.commit()


def section_roster(db: Session, section_id: int) -> List[Enrollment]:
    return db.query(Enrollment).join(User, User.id == Enrollment.student_id).filter(
        Enrollment.section_id == section_id, Enrollment.status == EnrollmentStatus.ENROLLED
    ).order_by(User.full_name).all()
