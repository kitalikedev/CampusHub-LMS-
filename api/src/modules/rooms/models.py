from sqlalchemy import CheckConstraint, Column, DateTime, SmallInteger, String

from src.core.db import Base, IdType
from src.core.time import utcnow


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (CheckConstraint("capacity > 0", name="ck_rooms_capacity"),)

    id = Column(IdType, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    capacity = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
