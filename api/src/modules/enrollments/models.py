from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from src.core.db import Base, IdType
from src.core.time import utcnow


class EnrollmentStatus:
    ENROLLED = "ENROLLED"
    DROPPED = "DROPPED"
    ALL = (ENROLLED, DROPPED)


class EnrollmentSource:
    SELF = "SELF"
    ADMIN = "ADMIN"
    ALL = (SELF, ADMIN)


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("section_id", "student_id", name="uq_enrollments_section_student"),  # BR-ENR-09
        Index("ix_enrollments_student_status", "student_id", "status"),
    )

    id = Column(IdType, primary_key=True, autoincrement=True)
    section_id = Column(IdType, ForeignKey("course_sections.id"), nullable=False)
    student_id = Column(IdType, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(*EnrollmentStatus.ALL, name="enrollment_status"), nullable=False)
    source = Column(Enum(*EnrollmentSource.ALL, name="enrollment_source"), nullable=False)
    override_reason = Column(Text, nullable=True)
    enrolled_at = Column(DateTime, nullable=False, default=utcnow)
    dropped_at = Column(DateTime, nullable=True)

    student = relationship("User", lazy="joined")
    result = relationship("CourseResult", uselist=False, back_populates="enrollment",
                          cascade="all, delete-orphan")


class CourseResult(Base):
    """Kết quả môn chốt lúc khóa sổ (BR-LCK-04, ADR-03)."""

    __tablename__ = "course_results"

    enrollment_id = Column(IdType, ForeignKey("enrollments.id", ondelete="CASCADE"), primary_key=True)
    final_score_10 = Column(Numeric(9, 6), nullable=False)
    letter_grade = Column(String(2), nullable=True)  # NULL với môn Non-Graded
    grade_point = Column(Numeric(3, 2), nullable=True)
    is_passed = Column(Boolean, nullable=False)
    finalized_at = Column(DateTime, nullable=False, default=utcnow)

    enrollment = relationship("Enrollment", back_populates="result")
