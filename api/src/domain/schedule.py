"""Kiểm tra trùng lịch theo khoảng nửa mở (BR-ACD-05)."""
from datetime import time
from typing import NamedTuple


class Slot(NamedTuple):
    day_of_week: int
    start: time
    end: time


def overlaps(a: Slot, b: Slot) -> bool:
    """08:00–10:00 và 10:00–12:00 không trùng."""
    return a.day_of_week == b.day_of_week and a.start < b.end and b.start < a.end
