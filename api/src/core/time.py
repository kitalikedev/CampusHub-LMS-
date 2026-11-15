"""Thời gian: lưu UTC (naive) trong DB, trả ISO 8601 kèm "Z" (BR-GEN-01, ISS-08)."""
from datetime import datetime, timezone
from typing import Optional

from pydantic import PlainSerializer
from typing_extensions import Annotated


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_naive_utc(value: Optional[datetime]) -> Optional[datetime]:
    """Chuẩn hóa về UTC không kèm tzinfo. Giá trị không có tzinfo được coi là UTC."""
    if value is None:
        return None
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def iso_z(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return to_naive_utc(value).replace(microsecond=0).isoformat() + "Z"


UTCDateTime = Annotated[datetime, PlainSerializer(iso_z, return_type=str)]
