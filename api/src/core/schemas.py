"""Kiểu dùng chung cho schema."""
from decimal import Decimal
from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, PlainSerializer
from typing_extensions import Annotated

T = TypeVar("T")

# Decimal trả về JSON dạng số (tính toán vẫn bằng Decimal ở backend).
Num = Annotated[Decimal, PlainSerializer(lambda v: float(v), return_type=float)]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int


class Message(BaseModel):
    ok: bool = True
