from typing import List

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user
from src.core.schemas import ORMModel
from src.core.time import UTCDateTime
from src.modules.announcements import service
from src.modules.users.models import User

router = APIRouter(tags=["announcements"])


class AnnouncementIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class AuthorBrief(ORMModel):
    id: int
    full_name: str


class AnnouncementOut(ORMModel):
    id: int
    section_id: int
    title: str
    content: str
    author: AuthorBrief
    created_at: UTCDateTime
    updated_at: UTCDateTime


@router.get("/sections/{section_id}/announcements", response_model=List[AnnouncementOut])
def list_announcements(section_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_for_section(db, user, section_id)


@router.post("/sections/{section_id}/announcements", response_model=AnnouncementOut, status_code=201)
def create_announcement(section_id: int, data: AnnouncementIn, db: Session = Depends(get_db),
                        user: User = Depends(get_current_user)):
    return service.create(db, user, section_id, data.title, data.content)


@router.patch("/announcements/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(announcement_id: int, data: AnnouncementIn, db: Session = Depends(get_db),
                        user: User = Depends(get_current_user)):
    return service.update(db, user, announcement_id, data.title, data.content)


@router.delete("/announcements/{announcement_id}", status_code=204)
def delete_announcement(announcement_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.delete(db, user, announcement_id)
    return Response(status_code=204)
