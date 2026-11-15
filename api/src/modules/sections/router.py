from typing import List, Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.modules.sections import service
from src.modules.sections.schemas import SectionIn, SectionOut, SectionUpdate, SlotIn
from src.modules.users.models import Role, User

router = APIRouter(tags=["sections"])
admin_only = require_roles(Role.ADMIN)


@router.get("/sections", response_model=List[SectionOut])
def list_sections(semester_id: Optional[int] = None, status: Optional[str] = None, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    return service.list_sections(db, user, semester_id, status)


@router.post("/sections", response_model=SectionOut, status_code=201)
def create_section(data: SectionIn, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    return service.section_out(db, service.create_section(db, data), admin)


@router.get("/sections/{section_id}", response_model=SectionOut)
def get_section(section_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    section = service.get_section(db, section_id)
    service.ensure_can_view(db, section, user)
    return service.section_out(db, section, user)


@router.patch("/sections/{section_id}", response_model=SectionOut)
def update_section(section_id: int, data: SectionUpdate, db: Session = Depends(get_db),
                   admin: User = Depends(admin_only)):
    return service.section_out(db, service.update_section(db, section_id, data), admin)


@router.post("/sections/{section_id}/publish", response_model=SectionOut)
def publish_section(section_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    return service.section_out(db, service.publish_section(db, section_id), admin)


@router.post("/sections/{section_id}/schedule-slots", response_model=SectionOut, status_code=201)
def add_slot(section_id: int, data: SlotIn, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    service.add_slot(db, section_id, data)
    return service.section_out(db, service.get_section(db, section_id), admin)


@router.delete("/schedule-slots/{slot_id}", status_code=204)
def delete_slot(slot_id: int, db: Session = Depends(get_db), _admin: User = Depends(admin_only)):
    service.delete_slot(db, slot_id)
    return Response(status_code=204)
