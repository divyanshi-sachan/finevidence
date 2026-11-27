import json

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


def test_rotation_keeps_one_extra_example_per_record_and_replays_facts(tmp_path):
    from finevidence.generation.self_training import (
        audit_verified_programs,
        load_verified_programs,
        self_training_examples,
    )

    record = {
        "id": "r1",
        "pre_text": ["revenue was 10 and costs were 5 , 4 and 2"],
        "post_text": [],
        "table": [["", "2009"], ["revenue", "$ 10"]],
        "qa": {
            "question": "ratio?",
            "program": "divide(10, 5)",
            "exe_ans": 2.0,
            "gold_inds": {"text_0": ""},
        },
    }
    path = tmp_path / "v.jsonl"
    rows = [
        {
            "record_id": "r1",
            "fact_keys": ["text_0"],
            "verified": ["divide(4, 2)", "subtract(4, 2)"],
        },
        {"record_id": "r2", "fact_keys": [], "verified": []},
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    verified = load_verified_programs(path)
    assert audit_verified_programs([record], verified, cap=4) == {
        "records_with_new_program": 1,
        "new_programs": 2,
    }
    with pytest.raises(ValueError):
        audit_verified_programs([record], verified, cap=4, excluded_ids={"r1"})
    targets = [self_training_examples([record], verified, epoch=e)[0].target for e in range(3)]
    assert targets == ["divide(4, 2)", "subtract(4, 2)", "divide(4, 2)"]
