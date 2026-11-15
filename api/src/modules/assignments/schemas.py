from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal

from src.core.schemas import Num, ORMModel
from src.core.time import UTCDateTime

ModeLiteral = Literal["SINGLE", "OVERWRITE", "MULTIPLE", "OFFLINE"]
LateLiteral = Literal["REJECT", "ACCEPT_MARK_LATE"]
VisibilityLiteral = Literal["IMMEDIATE", "MANUAL"]


class AssignmentIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    weight_percent: Decimal = Field(gt=0, le=100, decimal_places=2)
    submission_mode: ModeLiteral
    max_attempts: Optional[int] = Field(default=None, ge=1, le=20)
    due_at: Optional[datetime] = None
    late_policy: Optional[LateLiteral] = None
    grade_visibility: VisibilityLiteral = "IMMEDIATE"


class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    weight_percent: Optional[Decimal] = Field(default=None, gt=0, le=100, decimal_places=2)
    submission_mode: Optional[ModeLiteral] = None
    max_attempts: Optional[int] = Field(default=None, ge=1, le=20)
    due_at: Optional[datetime] = None
    late_policy: Optional[LateLiteral] = None
    grade_visibility: Optional[VisibilityLiteral] = None


class AssignmentOut(ORMModel):
    id: int
    section_id: int
    title: str
    description: Optional[str]
    weight_percent: Num
    submission_mode: str
    max_attempts: Optional[int]
    due_at: Optional[UTCDateTime]
    late_policy: Optional[str]
    grade_visibility: str
    grades_published_at: Optional[UTCDateTime]
    created_at: UTCDateTime
