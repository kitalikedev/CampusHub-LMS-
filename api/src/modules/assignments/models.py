from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Numeric, SmallInteger, String, Text

from src.core.db import Base, IdType
from src.core.time import utcnow


class SubmissionMode:
    SINGLE = "SINGLE"
    OVERWRITE = "OVERWRITE"
    MULTIPLE = "MULTIPLE"
    OFFLINE = "OFFLINE"
    ALL = (SINGLE, OVERWRITE, MULTIPLE, OFFLINE)


class LatePolicy:
    REJECT = "REJECT"
    ACCEPT_MARK_LATE = "ACCEPT_MARK_LATE"
    ALL = (REJECT, ACCEPT_MARK_LATE)


class GradeVisibility:
    IMMEDIATE = "IMMEDIATE"
    MANUAL = "MANUAL"
    ALL = (IMMEDIATE, MANUAL)


class Assignment(Base):
    """Một bài = một cột điểm (DEC-E1)."""

    __tablename__ = "assignments"
    __table_args__ = (
        CheckConstraint("weight_percent > 0 AND weight_percent <= 100", name="ck_assignments_weight"),
        CheckConstraint(
            "(submission_mode = 'OFFLINE' AND due_at IS NULL AND late_policy IS NULL) OR "
            "(submission_mode <> 'OFFLINE' AND due_at IS NOT NULL AND late_policy IS NOT NULL)",
            name="ck_assignments_offline",
        ),
        CheckConstraint(
            "(submission_mode = 'MULTIPLE' AND max_attempts IS NOT NULL AND max_attempts >= 1) OR "
            "(submission_mode <> 'MULTIPLE' AND max_attempts IS NULL)",
            name="ck_assignments_attempts",
        ),
    )

    id = Column(IdType, primary_key=True, autoincrement=True)
    section_id = Column(IdType, ForeignKey("course_sections.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    weight_percent = Column(Numeric(5, 2), nullable=False)
    submission_mode = Column(Enum(*SubmissionMode.ALL, name="submission_mode"), nullable=False)
    max_attempts = Column(SmallInteger, nullable=True)
    due_at = Column(DateTime, nullable=True)
    late_policy = Column(Enum(*LatePolicy.ALL, name="late_policy"), nullable=True)
    grade_visibility = Column(Enum(*GradeVisibility.ALL, name="grade_visibility"), nullable=False,
                              default=GradeVisibility.IMMEDIATE)
    grades_published_at = Column(DateTime, nullable=True)
    created_by = Column(IdType, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
