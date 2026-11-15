from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.core.schemas import Num, ORMModel
from src.core.time import UTCDateTime


class SemesterIn(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
    registration_start_at: datetime
    registration_end_at: datetime
    min_credits: int = Field(ge=0, le=60)
    max_credits: int = Field(ge=1, le=60)


class SemesterUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    registration_start_at: Optional[datetime] = None
    registration_end_at: Optional[datetime] = None
    min_credits: Optional[int] = Field(default=None, ge=0, le=60)
    max_credits: Optional[int] = Field(default=None, ge=1, le=60)


class SemesterOut(ORMModel):
    id: int
    code: str
    name: str
    start_date: date
    end_date: date
    registration_start_at: UTCDateTime
    registration_end_at: UTCDateTime
    min_credits: int
    max_credits: int
    is_registration_open: bool = False


class SubjectBrief(ORMModel):
    id: int
    code: str
    name: str
    credits: int
    is_graded: bool


class SubjectIn(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=255)
    credits: int = Field(ge=1, le=10)
    is_graded: bool = True
    description: Optional[str] = None


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    credits: Optional[int] = Field(default=None, ge=1, le=10)
    is_graded: Optional[bool] = None
    description: Optional[str] = None


class SubjectOut(SubjectBrief):
    description: Optional[str]
    prerequisites: List[SubjectBrief] = []


class PrerequisitesUpdate(BaseModel):
    prerequisite_ids: List[int]


class GradeScaleOut(ORMModel):
    letter: str
    min_score: Num
    grade_point: Num
    is_passing: bool
