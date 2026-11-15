"""Unit test cho src/domain (ví dụ Ex1–Ex6 ở 03 §5.3)."""
from datetime import datetime, time, timedelta
from decimal import Decimal

import pytest

from src.domain import grading as g
from src.domain.schedule import Slot, overlaps
from src.domain.submission_policy import PolicyViolation, decide

SCALE = [g.ScaleRow(l, Decimal(m), Decimal(p), ok) for l, m, p, ok in [
    ("A+", "9.0", "4.0", True), ("A", "8.5", "3.7", True), ("B+", "8.0", "3.5", True), ("B", "7.0", "3.0", True),
    ("C+", "6.5", "2.5", True), ("C", "5.5", "2.0", True), ("D+", "5.0", "1.5", True), ("F", "0.0", "0.0", False)]]
COLUMNS = [("9.0", 10), ("8.0", 20), ("8.5", 30), ("8.9", 40)]


def test_ex1_final_score_and_letter():  # TC-LCK-03
    score = g.final_score(COLUMNS)
    assert score == Decimal("8.61")
    assert g.to_letter(score, SCALE).letter == "A"


def test_ex2_missing_score_counts_zero():  # BR-LCK-02
    score = g.final_score([("9.0", 10), ("8.0", 20), (None, 30), ("8.9", 40)])
    assert score == Decimal("6.06")
    assert g.to_letter(score, SCALE).letter == "C"


@pytest.mark.parametrize("score,letter", [("8.4999", "B+"), ("4.9999", "F"), ("5.0", "D+"), ("10.0", "A+"),
                                          ("8.5", "A"), ("0", "F")])
def test_ex3_thresholds_without_rounding(score, letter):  # TC-TRN-01
    assert g.to_letter(score, SCALE).letter == letter


def _outcome(credits, score, letter, graded=True, passed=None):
    row = next(r for r in SCALE if r.letter == letter) if letter else None
    return g.CourseOutcome(credits, graded, Decimal(score), row.grade_point if row else None,
                           row.is_passing if row else passed)


def test_ex4_term_gpa():  # TC-TRN-02, TC-TRN-04
    outcomes = [_outcome(3, "8.61", "A"), _outcome(4, "7.45", "B"), _outcome(3, "4.80", "F"),
                _outcome(1, "8.0", None, graded=False, passed=True)]
    s = g.summarize(outcomes)
    assert (s.gpa, s.average_10, s.earned_credits, s.gpa_credits) == (Decimal("2.31"), Decimal("7.00"), 7, 10)


def test_ex5_cumulative_gpa_is_not_mean_of_terms():  # TC-TRN-03
    term1 = [_outcome(3, "8.61", "A"), _outcome(4, "7.45", "B"), _outcome(3, "4.80", "F")]
    term2 = [_outcome(3, "8.2", "B+"), _outcome(3, "9.5", "A+")]
    assert g.summarize(term2).gpa == Decimal("3.75")
    assert g.summarize(term1 + term2).gpa == Decimal("2.85")


def test_ex6_provisional_score():  # TC-GRD-05
    score, weight = g.provisional_score([(None, 10), ("8.0", 20), ("8.5", 30), (None, 40)])
    assert g.round_half_up(score) == Decimal("8.30") and weight == 50
    assert g.provisional_score([(None, 100)]) == (None, Decimal(0))


@pytest.mark.parametrize("value,expected", [("2.345", "2.35"), ("7.005", "7.01"), ("2.344", "2.34")])
def test_round_half_up(value, expected):  # TC-TRN-05
    assert g.round_half_up(value) == Decimal(expected)


def test_schedule_half_open_intervals():  # TC-ACD-03
    a = Slot(2, time(8), time(10))
    assert not overlaps(a, Slot(2, time(10), time(12)))
    assert overlaps(a, Slot(2, time(9, 30), time(11)))
    assert not overlaps(a, Slot(3, time(8), time(10)))


NOW = datetime(2026, 11, 9, 12, 0)


@pytest.mark.parametrize("mode,attempts,existing,code", [
    ("OFFLINE", None, 0, "SUBMISSION_NOT_ALLOWED"), ("SINGLE", None, 1, "SUBMISSION_LIMIT_REACHED"),
    ("MULTIPLE", 3, 3, "SUBMISSION_LIMIT_REACHED")])
def test_policy_violations(mode, attempts, existing, code):
    with pytest.raises(PolicyViolation) as exc:
        decide(mode, attempts, NOW + timedelta(days=1), "REJECT", NOW, existing, False)
    assert exc.value.code == code


def test_policy_late_and_overwrite():
    past = NOW - timedelta(hours=1)
    with pytest.raises(PolicyViolation) as exc:
        decide("SINGLE", None, past, "REJECT", NOW, 0, False)
    assert exc.value.code == "SUBMISSION_PAST_DUE"
    assert decide("SINGLE", None, past, "ACCEPT_MARK_LATE", NOW, 0, False).is_late
    assert decide("OVERWRITE", None, NOW + timedelta(1), "REJECT", NOW, 1, False).overwrite
    assert decide("MULTIPLE", 3, NOW + timedelta(1), "REJECT", NOW, 2, False).attempt_no == 3
    with pytest.raises(PolicyViolation) as exc:
        decide("OVERWRITE", None, NOW + timedelta(1), "REJECT", NOW, 1, True)
    assert exc.value.code == "SUBMISSION_ALREADY_GRADED"
