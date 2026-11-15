from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from src.core.db import Base, IdType
from src.core.time import utcnow


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(IdType, primary_key=True, autoincrement=True)
    section_id = Column(IdType, ForeignKey("course_sections.id"), nullable=False, index=True)
    author_id = Column(IdType, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    author = relationship("User", lazy="joined")
