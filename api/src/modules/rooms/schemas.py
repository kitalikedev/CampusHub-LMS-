from typing import Optional

from pydantic import BaseModel, Field

from src.core.schemas import ORMModel


class RoomIn(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0, le=1000)


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    capacity: Optional[int] = Field(default=None, gt=0, le=1000)


class RoomOut(ORMModel):
    id: int
    code: str
    name: str
    capacity: int
