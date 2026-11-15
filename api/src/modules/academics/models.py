from sqlalchemy import (Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Numeric,
                        SmallInteger, String, Table, Text)

from src.core.db import Base, IdType
from src.core.time import utcnow


class Semester(Base):
    __tablename__ = "semesters"
    __table_args__ = (
        CheckConstraint("start_date < end_date", name="ck_semesters_dates"),
        CheckConstraint("registration_start_at < registration_end_at", name="ck_semesters_registration"),
        CheckConstraint("min_credits <= max_credits", name="ck_semesters_credits"),
    )

    id = Column(IdType, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    registration_start_at = Column(DateTime, nullable=False)
    registration_end_at = Column(DateTime, nullable=False)
    min_credits = Column(SmallInteger, nullable=False)
    max_credits = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)


subject_prerequisites = Table(
    "subject_prerequisites",
    Base.metadata,
    Column("subject_id", IdType, ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
    Column("prerequisite_id", IdType, ForeignKey("subjects.id"), primary_key=True),
    CheckConstraint("subject_id <> prerequisite_id", name="ck_prereq_not_self"),
)


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (CheckConstraint("credits BETWEEN 1 AND 10", name="ck_subjects_credits"),)

    id = Column(IdType, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    credits = Column(SmallInteger, nullable=False)
    is_graded = Column(Boolean, nullable=False, default=True)  # False = Non-Graded (DEC-E5)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)


class GradeScale(Base):
    """Bảng quy đổi điểm, lưu dạng cấu hình (DEC-E2)."""

    __tablename__ = "grade_scales"

    id = Column(IdType, primary_key=True, autoincrement=True)
    letter = Column(String(2), nullable=False, unique=True)
    min_score = Column(Numeric(4, 2), nullable=False, unique=True)
    grade_point = Column(Numeric(3, 2), nullable=False)
    is_passing = Column(Boolean, nullable=False)
