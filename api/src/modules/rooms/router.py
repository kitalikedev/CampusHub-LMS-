from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.modules.rooms import service
from src.modules.rooms.schemas import RoomIn, RoomOut, RoomUpdate
from src.modules.users.models import Role, User

router = APIRouter(prefix="/rooms", tags=["rooms"])
admin_only = require_roles(Role.ADMIN)


@router.get("", response_model=List[RoomOut])
def list_rooms(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return service.list_rooms(db)


@router.post("", response_model=RoomOut, status_code=201)
def create_room(data: RoomIn, db: Session = Depends(get_db), _admin: User = Depends(admin_only)):
    return service.create_room(db, data)


@router.patch("/{room_id}", response_model=RoomOut)
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db), _admin: User = Depends(admin_only)):
    return service.update_room(db, room_id, data)


@router.delete("/{room_id}", status_code=204)
def delete_room(room_id: int, db: Session = Depends(get_db), _admin: User = Depends(admin_only)):
    service.delete_room(db, room_id)
    return Response(status_code=204)
