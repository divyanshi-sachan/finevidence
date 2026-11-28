import pytest

from finevidence.generation.rule_selection import rejection_reason, select_by_rules

TABLE = [["", "2009", "2008"], ["revenue", "$ 10", "$ 5"]]
FACTS = ("the revenue of 2009 is $ 10 ; 2008 is $ 5",)


def test_each_rule_names_its_reason():
    assert rejection_reason(None, FACTS, TABLE) == "malformed"
    assert rejection_reason("divide(10,", FACTS, TABLE) == "malformed"
    assert rejection_reason("divide(10, 0)", FACTS, TABLE) == "execution"
    assert rejection_reason("add(#1, 5)", FACTS, TABLE) == "execution"
    assert rejection_reason("divide(10, 4)", FACTS, TABLE) == "ungrounded_literal"
    assert rejection_reason("table_sum(revenue, none)", ("costs were 5",), TABLE) == (
        "table_row_not_in_facts"
    )
    assert rejection_reason("subtract(10, 5), divide(#0, 5)", FACTS, TABLE) is None


def test_selects_highest_scoring_survivor_or_falls_back():
    chosen = select_by_rules(
        ["divide(10, 4)", "divide(10, 5)", "subtract(10, 5)"], [-0.1, -0.3, -0.2], FACTS, TABLE
    )
    assert (chosen.index, chosen.fallback) == (2, False)
    assert chosen.rejections == ("ungrounded_literal", None, None)
    fallback = select_by_rules(["divide(10, 0)", None], [-0.5, -0.1], FACTS, TABLE)
    assert (fallback.index, fallback.fallback) == (0, True)
    with pytest.raises(ValueError):
        select_by_rules([], [], FACTS, TABLE)
