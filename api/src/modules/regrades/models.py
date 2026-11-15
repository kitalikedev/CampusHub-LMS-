from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, Text

from src.core.db import Base, IdType
from src.core.time import utcnow


class RegradeStatus:
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ALL = (PENDING, ACCEPTED, REJECTED)


class RegradeRequest(Base):
    __tablename__ = "regrade_requests"

    id = Column(IdType, primary_key=True, autoincrement=True)
    grade_id = Column(IdType, ForeignKey("grades.id"), nullable=False, unique=True)  # BR-REG-02
    reason = Column(Text, nullable=False)
    status = Column(Enum(*RegradeStatus.ALL, name="regrade_status"), nullable=False, default=RegradeStatus.PENDING)
    old_score = Column(Numeric(4, 2), nullable=False)
    new_score = Column(Numeric(4, 2), nullable=True)
    response = Column(Text, nullable=True)
    resolved_by = Column(IdType, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    resolved_at = Column(DateTime, nullable=True)
