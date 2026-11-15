from datetime import time
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.core.schemas import Num
from src.modules.academics.schemas import SemesterOut
from src.modules.announcements.router import AnnouncementOut
from src.modules.assignments.schemas import AssignmentOut
from src.modules.sections.schemas import SectionOut
from src.modules.transcripts import service
from src.modules.users.models import Role, User
from src.modules.users.schemas import UserBrief

router = APIRouter(prefix="/me", tags=["me"])


class TranscriptCourse(BaseModel):
    section_id: int
    section_code: str
    subject_code: str
    subject_name: str
    credits: int
    is_graded: bool
    status: str
    score_10: Optional[Num]
    letter_grade: Optional[str]
    grade_point: Optional[Num]
    is_passed: Optional[bool]
    provisional_score: Optional[Num]
    graded_weight: Optional[Num]


class TermSummary(BaseModel):
    semester: SemesterOut
    courses: List[TranscriptCourse]
    gpa: Optional[Num]
    average_10: Optional[Num]
    gpa_credits: int
    earned_credits: int


class Cumulative(BaseModel):
    gpa: Optional[Num]
    average_10: Optional[Num]
    gpa_credits: int
    earned_credits: int


class Transcript(BaseModel):
    student: UserBrief
    semesters: List[TermSummary]
    cumulative: Cumulative


class ScheduleItem(BaseModel):
    section_id: int
    section_code: str
    subject_code: str
    subject_name: str
    instructor_name: str
    day_of_week: int
    start_time: time
    end_time: time
    room_code: str


class MySchedule(BaseModel):
    semester: Optional[SemesterOut]
    items: List[ScheduleItem]


class UpcomingItem(BaseModel):
    assignment: AssignmentOut
    section_code: str
    status: str


class Dashboard(BaseModel):
    semester: Optional[SemesterOut]
    sections: List[SectionOut]
    announcements: List[AnnouncementOut]
    upcoming: List[UpcomingItem]
    pending_grading: Optional[int]
    pending_regrades: Optional[int]


@router.get("/transcript", response_model=Transcript)
def transcript(db: Session = Depends(get_db), user: User = Depends(require_roles(Role.STUDENT))):
    return service.transcript(db, user)


@router.get("/schedule", response_model=MySchedule)
def schedule(semester_id: Optional[int] = None, db: Session = Depends(get_db),
             user: User = Depends(require_roles(Role.STUDENT, Role.INSTRUCTOR))):
    return service.schedule(db, user, semester_id)


@router.get("/sections", response_model=List[SectionOut])
def my_sections(semester_id: Optional[int] = None, db: Session = Depends(get_db),
                user: User = Depends(require_roles(Role.STUDENT, Role.INSTRUCTOR))):
    return service.my_sections(db, user, semester_id)


@router.get("/dashboard", response_model=Dashboard)
def dashboard(db: Session = Depends(get_db), user: User = Depends(require_roles(Role.STUDENT, Role.INSTRUCTOR))):
    return service.dashboard(db, user)
