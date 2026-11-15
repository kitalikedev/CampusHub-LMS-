from datetime import time
from typing import List, Optional

from pydantic import BaseModel, Field

from src.core.schemas import ORMModel
from src.core.time import UTCDateTime
from src.modules.academics.schemas import SubjectBrief
from src.modules.rooms.schemas import RoomOut


class SlotIn(BaseModel):
    room_id: int
    day_of_week: int = Field(ge=1, le=7)
    start_time: time
    end_time: time


class SlotOut(ORMModel):
    id: int
    day_of_week: int
    start_time: time
    end_time: time
    room: RoomOut


class SectionIn(BaseModel):
    semester_id: int
    subject_id: int
    section_code: str = Field(min_length=1, max_length=20)
    instructor_id: int
    capacity: int = Field(gt=0, le=1000)


class SectionUpdate(BaseModel):
    section_code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    instructor_id: Optional[int] = None
    capacity: Optional[int] = Field(default=None, gt=0, le=1000)


class SemesterBrief(ORMModel):
    id: int
    code: str
    name: str


class InstructorBrief(ORMModel):
    id: int
    full_name: str
    email: str


class SectionOut(BaseModel):
    id: int
    section_code: str
    status: str
    capacity: int
    enrolled_count: int
    semester: SemesterBrief
    subject: SubjectBrief
    prerequisites: List[SubjectBrief] = []
    instructor: InstructorBrief
    slots: List[SlotOut]
    locked_at: Optional[UTCDateTime] = None
    is_enrolled: Optional[bool] = None  # chỉ có khi người xem là SV
    registration_open: bool = False
