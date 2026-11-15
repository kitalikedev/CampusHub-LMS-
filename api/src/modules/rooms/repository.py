"""Truy vấn phòng học. Không commit (ADR-05)."""
from typing import List, Optional

from sqlalchemy.orm import Session

from src.modules.rooms.models import Room
from src.modules.sections.models import ScheduleSlot


def list_all(db: Session) -> List[Room]:
    return db.query(Room).order_by(Room.code).all()


def get(db: Session, room_id: int) -> Optional[Room]:
    return db.get(Room, room_id)


def get_by_code(db: Session, code: str) -> Optional[Room]:
    return db.query(Room).filter(Room.code == code).first()


def is_in_use(db: Session, room_id: int) -> bool:
    return db.query(ScheduleSlot.id).filter(ScheduleSlot.room_id == room_id).first() is not None


def add(db: Session, room: Room) -> Room:
    db.add(room)
    db.flush()
    return room


def delete(db: Session, room: Room) -> None:
    db.delete(room)
