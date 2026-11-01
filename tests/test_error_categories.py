from finevidence.evaluation import CATEGORIES, categorize_error

TABLE = [
    ["", "2009", "2008", "2007"],
    ["revenue", "$ 120", "$ 100", "$ 90"],
    ["cost", "$ 60", "$ 50", "$ 45"],
]
GOLD = "subtract(120, 100), divide(#0, 100)"


def _categorize(program, value, *, input_keys=("table_1", "table_2")):
    return categorize_error(
        predicted_program=program,
        predicted_value=value,
        reference_value=0.2,
        gold_program=GOLD,
        gold_keys={"table_1"},
        input_keys=set(input_keys),
        table=TABLE,
    )


def test_invalid_program_comes_first():
    assert _categorize(None, None, input_keys=()).primary == "invalid_program"


def test_missing_gold_fact_is_a_retrieval_miss():
    assert _categorize(GOLD, 20.0, input_keys=("table_2",)).primary == "retrieval_miss"


def test_scale_sign_and_near_miss():
    assert _categorize("subtract(120, 100), divide(#0, 1)", 20.0).primary == "scale_error"
    assert _categorize("subtract(100, 120), divide(#0, 100)", -0.2).primary == "sign_error"
    assert _categorize("subtract(120, 100), divide(#0, 101)", 0.19802).primary == "near_miss"


def test_operation_error_when_steps_differ():
    assert _categorize("divide(120, 100)", 1.2).primary == "operation_error"


def test_operand_error_details():
    wrong_year = _categorize("subtract(120, 90), divide(#0, 90)", 0.33333)
    assert wrong_year.primary == "operand_error"
    assert wrong_year.operand_detail == "same_table_row_as_gold"
    wrong_row = _categorize("subtract(60, 50), divide(#0, 50)", 0.2 * 1.7)
    assert wrong_row.operand_detail == "other_value"


def test_categories_are_listed_in_priority_order():
    assert CATEGORIES[0] == "invalid_program" and CATEGORIES[-1] == "other"
