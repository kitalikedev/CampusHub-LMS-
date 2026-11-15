from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, SmallInteger, String,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from src.core.db import Base, IdType
from src.core.time import utcnow


class StoredFile(Base):
    __tablename__ = "files"

    id = Column(IdType, primary_key=True, autoincrement=True)
    uploaded_by = Column(IdType, ForeignKey("users.id"), nullable=False)
    original_name = Column(String(255), nullable=False)
    stored_path = Column(String(500), nullable=False, unique=True)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("assignment_id", "student_id", "attempt_no", name="uq_submissions_attempt"),  # BR-SUB-08
        CheckConstraint("content_url IS NOT NULL OR file_id IS NOT NULL", name="ck_submissions_content"),
    )

    id = Column(IdType, primary_key=True, autoincrement=True)
    assignment_id = Column(IdType, ForeignKey("assignments.id"), nullable=False, index=True)
    student_id = Column(IdType, ForeignKey("users.id"), nullable=False)
    attempt_no = Column(SmallInteger, nullable=False, default=1)
    content_url = Column(String(2048), nullable=True)
    file_id = Column(IdType, ForeignKey("files.id"), nullable=True, unique=True)
    is_late = Column(Boolean, nullable=False, default=False)
    submitted_at = Column(DateTime, nullable=False, default=utcnow)

    file = relationship("StoredFile", lazy="joined")
