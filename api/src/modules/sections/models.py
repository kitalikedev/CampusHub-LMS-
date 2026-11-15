from sqlalchemy import (CheckConstraint, Column, DateTime, Enum, ForeignKey, SmallInteger, String, Time,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from src.core.db import Base, IdType
from src.core.time import utcnow


class SectionStatus:
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    LOCKED = "LOCKED"
    ALL = (DRAFT, PUBLISHED, LOCKED)


class CourseSection(Base):
    __tablename__ = "course_sections"
    __table_args__ = (
        UniqueConstraint("semester_id", "section_code", name="uq_sections_semester_code"),
        CheckConstraint("capacity > 0", name="ck_sections_capacity"),
    )

    id = Column(IdType, primary_key=True, autoincrement=True)
    semester_id = Column(IdType, ForeignKey("semesters.id"), nullable=False, index=True)
    subject_id = Column(IdType, ForeignKey("subjects.id"), nullable=False)
    section_code = Column(String(20), nullable=False)
    instructor_id = Column(IdType, ForeignKey("users.id"), nullable=False)
    capacity = Column(SmallInteger, nullable=False)
    status = Column(Enum(*SectionStatus.ALL, name="section_status"), nullable=False, default=SectionStatus.DRAFT)
    locked_at = Column(DateTime, nullable=True)
    locked_by = Column(IdType, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    semester = relationship("Semester", lazy="joined")
    subject = relationship("Subject", lazy="joined")
    instructor = relationship("User", foreign_keys=[instructor_id], lazy="joined")
    slots = relationship("ScheduleSlot", back_populates="section", cascade="all, delete-orphan",
                         order_by="(ScheduleSlot.day_of_week, ScheduleSlot.start_time)")


class ScheduleSlot(Base):
    """Giờ học là giờ địa phương theo lịch trường, không quy đổi múi giờ (BR-GEN-01)."""

    __tablename__ = "schedule_slots"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="ck_slots_day"),
        CheckConstraint("start_time < end_time", name="ck_slots_time"),
    )

    id = Column(IdType, primary_key=True, autoincrement=True)
    section_id = Column(IdType, ForeignKey("course_sections.id", ondelete="CASCADE"), nullable=False, index=True)
    room_id = Column(IdType, ForeignKey("rooms.id"), nullable=False)
    day_of_week = Column(SmallInteger, nullable=False)  # 1 = Thứ Hai … 7 = Chủ nhật
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    section = relationship("CourseSection", back_populates="slots")
    room = relationship("Room", lazy="joined")
