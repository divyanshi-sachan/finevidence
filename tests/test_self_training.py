import pytest

from finevidence.generation.self_training import select_verified_programs

RECORD = {
    "id": "r1",
    "table": [["", "2009"], ["revenue", "$ 10"]],
    "qa": {"program": "divide(10, 5)", "exe_ans": 2.0},
}
FACTS = ("revenue was 10 and costs were 5 , 4 and 2",)


def test_keeps_distinct_correct_grounded_programs_other_than_gold():
    candidates = [
        "divide(10, 5)",  # gold
        "divide(4, 2)",  # correct, grounded
        "divide(4,  2)",  # duplicate after normalisation
        "subtract(4, 2)",  # correct value, grounded
        "divide(8, 4)",  # correct value, 8 not in facts
        "add(1, 1)",  # correct value, 1 not in facts
        "divide(10, 2)",  # wrong value
        None,
    ]
    assert select_verified_programs(RECORD, candidates, FACTS, cap=5) == [
        "divide(4, 2)",
        "subtract(4, 2)",
    ]


def test_cap_limits_kept_programs():
    assert select_verified_programs(RECORD, ["divide(4, 2)", "subtract(4, 2)"], FACTS, cap=1) == [
        "divide(4, 2)"
    ]
    with pytest.raises(ValueError):
        select_verified_programs(RECORD, [], FACTS, cap=0)
