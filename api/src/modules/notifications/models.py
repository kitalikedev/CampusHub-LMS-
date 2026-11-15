from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Index, String

from src.core.db import Base, IdType
from src.core.time import utcnow


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_read", "user_id", "is_read", "created_at"),)

    id = Column(IdType, primary_key=True, autoincrement=True)
    user_id = Column(IdType, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)
    params = Column(JSON, nullable=False)
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)
