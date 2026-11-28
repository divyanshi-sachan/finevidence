import pytest

from finevidence.generation.reranker import FEATURE_NAMES, beam_features

TABLE = [["", "2009"], ["revenue", "$ 10"]]
FACTS = ("revenue was 10 and costs were 5",)


def test_features_describe_each_beam():
    rows = beam_features(
        ["divide(10, 5)", "divide(10, 0)", "add(10, 4)"],
        [-0.1, -0.3, -0.4],
        ["divide(10, 5)", "subtract(7, 5)", "divide(10, 0)", "add(1, 1)"],
        FACTS,
        TABLE,
    )
    named = [dict(zip(FEATURE_NAMES, row, strict=True)) for row in rows]
    assert named[0]["executes"] == 1.0 and named[0]["grounded"] == 1.0
    assert named[0]["sample_agreement"] == 0.75  # value 2.0: divide(10,5), subtract(7,5), add(1,1)
    assert named[1]["executes"] == 0.0 and named[1]["beam_agreement"] == 0.0
    assert named[2]["grounded"] == 0.0 and named[2]["gap_to_top"] == pytest.approx(-0.3)


def test_rejects_mismatched_inputs():
    with pytest.raises(ValueError):
        beam_features(["divide(10, 5)"], [], ["divide(10, 5)"], FACTS, TABLE)
