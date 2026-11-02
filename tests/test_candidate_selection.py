import pytest

from finevidence.generation import is_grounded_and_executable, select_grounded_candidate

FACTS = ["the revenue of 2009 is $ 14669 ; the revenue of 2008 is $ 1526 ;"]
TABLE = [["", "2009", "2008"], ["revenue", "$ 14669", "$ 1526"]]


def test_copy_error_is_not_grounded():
    assert not is_grounded_and_executable("divide(1526, 14699)", FACTS, TABLE)
    assert is_grounded_and_executable("divide(1526, 14669)", FACTS, TABLE)


def test_constants_and_references_need_no_grounding():
    assert is_grounded_and_executable("subtract(14669, 1526), divide(#0, const_100)", FACTS, TABLE)


def test_unparseable_or_failing_programs_are_skipped():
    assert not is_grounded_and_executable("divide(1526 14669)", FACTS, TABLE)
    assert not is_grounded_and_executable("divide(#3, 1526)", FACTS, TABLE)


def test_selects_first_grounded_candidate_in_beam_order():
    candidates = ["divide(1526, 14699)", "divide(1526, 14669)", "divide(14669, 1526)"]
    assert select_grounded_candidate(candidates, FACTS, TABLE) == 1


def test_falls_back_to_top_beam():
    assert select_grounded_candidate(["divide(1, 2)", "divide(3, 4)"], FACTS, TABLE) == 0
    with pytest.raises(ValueError):
        select_grounded_candidate([], FACTS, TABLE)
