"""Phòng học (BR-ACD-06). Module mẫu: router mỏng → service kiểm tra rule + commit → repository truy vấn."""
from typing import List

from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.modules.rooms import repository as repo
from src.modules.rooms.models import Room
from src.modules.rooms.schemas import RoomIn, RoomUpdate
from src.modules.sections.models import CourseSection, ScheduleSlot


def list_rooms(db: Session) -> List[Room]:
    return repo.list_all(db)


def get_room(db: Session, room_id: int) -> Room:
    room = repo.get(db, room_id)
    if room is None:
        raise AppError("NOT_FOUND")
    return room


def create_room(db: Session, data: RoomIn) -> Room:
    code = data.code.strip().upper()
    if repo.get_by_code(db, code):
        raise AppError("VALIDATION_ERROR", {"field": "code", "reason": "DUPLICATE"})
    room = repo.add(db, Room(code=code, name=data.name.strip(), capacity=data.capacity))
    db.commit()
    return room


def update_room(db: Session, room_id: int, data: RoomUpdate) -> Room:
    room = get_room(db, room_id)
    if data.capacity is not None and data.capacity < room.capacity:
        # Sức chứa phòng vẫn phải ≥ sĩ số các lớp đang dùng phòng (BR-ACD-05).
        biggest = db.query(CourseSection.capacity).join(ScheduleSlot, ScheduleSlot.section_id == CourseSection.id) \
            .filter(ScheduleSlot.room_id == room.id).order_by(CourseSection.capacity.desc()).first()
        if biggest and biggest[0] > data.capacity:
            raise AppError("ROOM_CAPACITY_TOO_SMALL", {"room_code": room.code, "required": biggest[0]})
        room.capacity = data.capacity
    elif data.capacity is not None:
        room.capacity = data.capacity
    if data.name is not None:
        room.name = data.name.strip()
    db.commit()
    return room


def delete_room(db: Session, room_id: int) -> None:
    room = get_room(db, room_id)
    if repo.is_in_use(db, room.id):
        raise AppError("ROOM_IN_USE", {"room_code": room.code})
    repo.delete(db, room)
    db.commit()
