from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Numeric, Text, UniqueConstraint

from src.core.db import Base, IdType
from src.core.time import utcnow


class Grade(Base):
    """Điểm của một SV cho một bài, tách khỏi bài nộp (ADR-02, BR-GRD-02)."""

    __tablename__ = "grades"
    __table_args__ = (
        UniqueConstraint("assignment_id", "student_id", name="uq_grades_assignment_student"),
        CheckConstraint("score >= 0 AND score <= 10", name="ck_grades_score"),
    )

    id = Column(IdType, primary_key=True, autoincrement=True)
    assignment_id = Column(IdType, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(IdType, ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Numeric(4, 2), nullable=False)
    feedback = Column(Text, nullable=True)
    graded_by = Column(IdType, ForeignKey("users.id"), nullable=False)
    graded_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    visible_at = Column(DateTime, nullable=True)  # lúc SV bắt đầu thấy điểm (BR-GRD-04)
