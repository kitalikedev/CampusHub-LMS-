"""Phân quyền theo tài nguyên (BR-GEN-02, ma trận 05 §5)."""
from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.modules.enrollments.models import Enrollment, EnrollmentStatus
from src.modules.sections.models import CourseSection, SectionStatus
from src.modules.users.models import Role, User


def ensure_admin(user: User) -> None:
    if user.role != Role.ADMIN:
        raise AppError("FORBIDDEN")


def is_section_instructor(section: CourseSection, user: User) -> bool:
    return user.role == Role.INSTRUCTOR and section.instructor_id == user.id


def ensure_section_instructor(section: CourseSection, user: User) -> None:
    if not is_section_instructor(section, user):
        raise AppError("NOT_SECTION_INSTRUCTOR")


def is_enrolled(db: Session, section_id: int, student_id: int) -> bool:
    return db.query(Enrollment.id).filter(
        Enrollment.section_id == section_id,
        Enrollment.student_id == student_id,
        Enrollment.status == EnrollmentStatus.ENROLLED,
    ).first() is not None


def ensure_enrolled(db: Session, section: CourseSection, user: User) -> None:
    if user.role != Role.STUDENT or not is_enrolled(db, section.id, user.id):
        raise AppError("NOT_ENROLLED")


def ensure_section_member(db: Session, section: CourseSection, user: User) -> None:
    """Admin, GV phụ trách hoặc SV đang học trong lớp."""
    if user.role == Role.ADMIN:
        return
    if user.role == Role.INSTRUCTOR:
        ensure_section_instructor(section, user)
        return
    ensure_enrolled(db, section, user)


def ensure_not_locked(section: CourseSection) -> None:
    if section.status == SectionStatus.LOCKED:
        raise AppError("SECTION_LOCKED")
