from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, Index, String, Text

from src.core.db import Base, IdType
from src.core.time import utcnow


class AuditLog(Base):
    """Nhật ký chỉ thêm, không sửa/xóa (BR-AUD-01)."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_created", "created_at"),
    )

    id = Column(IdType, primary_key=True, autoincrement=True)
    actor_id = Column(IdType, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(BigInteger, nullable=False)
    before_data = Column(JSON, nullable=True)
    after_data = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
