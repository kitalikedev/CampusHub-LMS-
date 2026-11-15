"""Tính điểm môn, quy đổi, GPA (03 §5). Hàm thuần, không đụng DB (ADR-04)."""
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable, List, NamedTuple, Optional, Sequence, Tuple, Union

Number = Union[Decimal, int, float, str]
NON_GRADED_PASS_SCORE = Decimal("5.0")  # BR-LCK-05 (ĐỀ XUẤT, OQ-06)


def dec(value: Number) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def round_half_up(value: Number, places: int = 2) -> Decimal:
    """Làm tròn half-up, chỉ dùng cho kết quả cuối (BR-TRN-06)."""
    return dec(value).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


class ScaleRow(NamedTuple):
    letter: str
    min_score: Decimal
    grade_point: Decimal
    is_passing: bool


def final_score(items: Iterable[Tuple[Optional[Number], Number]]) -> Decimal:
    """Điểm môn khi khóa sổ: bài thiếu điểm tính 0, không làm tròn (BR-LCK-02).

    items: (điểm 0–10 hoặc None, trọng số %).
    """
    total = sum((dec(score or 0) * dec(weight) for score, weight in items), Decimal(0))
    return total / Decimal(100)


def provisional_score(items: Iterable[Tuple[Optional[Number], Number]]) -> Tuple[Optional[Decimal], Decimal]:
    """Điểm tạm tính trên các bài đã có điểm (BR-GRD-05). Trả (điểm hoặc None, % trọng số đã có điểm)."""
    graded = [(dec(s), dec(w)) for s, w in items if s is not None]
    weight = sum((w for _, w in graded), Decimal(0))
    if weight == 0:
        return None, Decimal(0)
    return sum((s * w for s, w in graded), Decimal(0)) / weight, weight


def to_letter(score: Number, scales: Sequence[ScaleRow]) -> ScaleRow:
    """Chọn bậc có ngưỡng dưới lớn nhất ≤ điểm, so trực tiếp với điểm gốc (BR-LCK-03)."""
    value = dec(score)
    ordered = sorted(scales, key=lambda r: r.min_score, reverse=True)
    for row in ordered:
        if value >= row.min_score:
            return row
    return ordered[-1]


class CourseOutcome(NamedTuple):
    credits: int
    is_graded: bool
    score_10: Decimal
    grade_point: Optional[Decimal]
    is_passed: bool


class Summary(NamedTuple):
    gpa: Optional[Decimal]
    average_10: Optional[Decimal]
    gpa_credits: int
    earned_credits: int


def summarize(outcomes: Iterable[CourseOutcome]) -> Summary:
    """GPA/TBC theo trọng số tín chỉ; F tính 0; Non-Graded không tính (BR-TRN-02…05, 07)."""
    rows: List[CourseOutcome] = [o for o in outcomes if o.is_graded]
    credits = sum(o.credits for o in rows)
    earned = sum(o.credits for o in rows if o.is_passed)
    if credits == 0:
        return Summary(None, None, 0, earned)
    gpa = sum((dec(o.grade_point or 0) * o.credits for o in rows), Decimal(0)) / credits
    avg = sum((dec(o.score_10) * o.credits for o in rows), Decimal(0)) / credits
    return Summary(round_half_up(gpa), round_half_up(avg), credits, earned)
