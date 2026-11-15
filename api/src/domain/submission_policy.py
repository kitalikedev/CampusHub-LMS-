"""Quyết định một lần nộp có hợp lệ không (03 §4, bảng §7.2, §7.3)."""
from datetime import datetime
from typing import NamedTuple, Optional


class PolicyViolation(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class Decision(NamedTuple):
    attempt_no: int
    is_late: bool
    overwrite: bool  # True: thay bản attempt 1 hiện có (OVERWRITE)


def is_late(submitted_at: datetime, due_at: Optional[datetime]) -> bool:
    return due_at is not None and submitted_at > due_at


def decide(mode: str, max_attempts: Optional[int], due_at: Optional[datetime], late_policy: Optional[str],
           now: datetime, existing_attempts: int, has_grade: bool) -> Decision:
    if mode == "OFFLINE":
        raise PolicyViolation("SUBMISSION_NOT_ALLOWED")  # BR-SUB-01
    if has_grade:
        raise PolicyViolation("SUBMISSION_ALREADY_GRADED")  # BR-SUB-07
    late = is_late(now, due_at)
    if late and late_policy == "REJECT":
        raise PolicyViolation("SUBMISSION_PAST_DUE")  # BR-SUB-03
    if mode == "SINGLE":
        if existing_attempts >= 1:
            raise PolicyViolation("SUBMISSION_LIMIT_REACHED")  # BR-SUB-04
        return Decision(1, late, False)
    if mode == "OVERWRITE":
        return Decision(1, late, existing_attempts >= 1)  # BR-SUB-05
    if mode == "MULTIPLE":
        if existing_attempts >= (max_attempts or 1):
            raise PolicyViolation("SUBMISSION_LIMIT_REACHED")  # BR-SUB-06
        return Decision(existing_attempts + 1, late, False)
    raise PolicyViolation("SUBMISSION_NOT_ALLOWED")
