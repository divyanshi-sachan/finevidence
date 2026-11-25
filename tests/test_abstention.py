import pytest

from finevidence.evaluation.abstention import candidate_agreement, coverage_curve

TABLE = [["", "2009"], ["revenue", "$ 10"]]


def test_agreement_counts_candidates_with_the_same_value():
    candidates = ["divide(4, 2)", "add(1, 1)", "subtract(5, 1)", "divide(4, 0)"]
    assert candidate_agreement(candidates, TABLE, 0) == 0.5
    assert candidate_agreement(candidates, TABLE, 2) == 0.25


def test_invalid_chosen_candidate_has_zero_confidence():
    assert candidate_agreement(["divide(4, 0)", "add(1, 1)"], TABLE, 0) == 0.0
    with pytest.raises(ValueError):
        candidate_agreement([], TABLE, 0)


def test_coverage_curve_answers_at_or_above_threshold():
    points = coverage_curve([1.0, 1.0, 0.5, 0.25], [True, True, False, True])
    assert [(p.threshold, p.answered) for p in points] == [(1.0, 2), (0.5, 3), (0.25, 4)]
    assert points[0].accuracy == 1.0 and points[0].coverage == 0.5
    assert points[-1].accuracy == 0.75
