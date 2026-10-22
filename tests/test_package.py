import hashlib
import io
import json
from decimal import Decimal
from pathlib import Path

import pytest

from finevidence import __version__
from finevidence.data import (
    FORBIDDEN_INFERENCE_FIELDS,
    acquisition,
    assert_inference_safe,
    audit_record_annotations,
    build_structured_input,
    load_finqa_split,
    normalize_financial_value,
    parse_finqa_program,
    serialize_table_for_retrieval,
    validate_evidence_key,
    validate_records,
)
from finevidence.evaluation import (
    ComparisonStatus,
    compare_display_answers,
    compare_execution,
    compare_programs,
    gold_recall_at_k,
    parse_display_answer,
)
from finevidence.reasoning import (
    Intent,
    NumericCandidate,
    Operation,
    classify_intent,
    execute_program,
    official_str_to_num,
    parse_numeric_candidate,
    reason_over_candidates,
)
from finevidence.retrieval import (
    build_evidence_segments,
    load_retriever_config,
    segment_numeric_candidates,
)


def test_package_imports() -> None:
    assert __version__ == "0.1.0"


def test_validation_reports_non_mapping_records() -> None:
    assert validate_records([{"question": "What is revenue?"}, "invalid"]) == [
        "Record 1 is not a mapping."
    ]


def test_load_finqa_split_accepts_object_records(tmp_path) -> None:
    split_path = tmp_path / "train.json"
    split_path.write_text(json.dumps([{"id": "example-1", "qa": {}}]), encoding="utf-8")

    assert load_finqa_split(split_path) == [{"id": "example-1", "qa": {}}]


def test_load_finqa_split_rejects_non_object_records(tmp_path) -> None:
    split_path = tmp_path / "invalid.json"
    split_path.write_text(json.dumps(["not an object"]), encoding="utf-8")

    with pytest.raises(ValueError, match="non-object records"):
        load_finqa_split(split_path)


def test_validate_evidence_key_accepts_observed_table_and_text_keys() -> None:
    assert validate_evidence_key("table_3", text_count=10, table_count=4).is_valid
    assert validate_evidence_key("text_9", text_count=10, table_count=4).is_valid


def test_validate_evidence_key_flags_negative_and_out_of_range_indices() -> None:
    negative = validate_evidence_key("text_-1", text_count=24, table_count=3)
    out_of_range = validate_evidence_key("table_3", text_count=24, table_count=3)

    assert (negative.is_valid, negative.reason) == (False, "index outside source bounds")
    assert (out_of_range.is_valid, out_of_range.reason) == (False, "index outside source bounds")


def test_parse_finqa_program_parses_constants_and_intermediate_references() -> None:
    result = parse_finqa_program("subtract(51%, 20%), divide(343, #0)")

    assert result.is_valid
    assert result.steps[0].arguments == ("51%", "20%")
    assert result.steps[1].arguments == ("343", "#0")


def test_parse_finqa_program_rejects_untrusted_syntax_without_execution() -> None:
    result = parse_finqa_program("__import__('os').system('echo unsafe')")

    assert not result.is_valid
    assert result.steps == ()


def test_normalize_financial_value_preserves_raw_and_recognizes_context_free_surface() -> None:
    candidate = normalize_financial_value(
        "($1,250.50)%, million", local_context="amount in millions"
    )

    assert candidate.raw == "($1,250.50)%, million"
    assert candidate.status == "unsupported"
    assert candidate.local_context == "amount in millions"


def test_normalize_financial_value_recognizes_sign_currency_percent_and_scale() -> None:
    candidate = normalize_financial_value("($1,250.50) million")

    assert candidate.raw == "($1,250.50) million"
    assert candidate.status == "recognized"
    assert candidate.numeric_token == "1,250.50"
    assert candidate.sign_style == "accounting_parentheses"
    assert candidate.currency_symbol == "$"
    assert candidate.percent_marker is False
    assert candidate.scale_word == "million"


def test_normalize_financial_value_handles_leading_decimal_and_ambiguous_forms() -> None:
    leading_decimal = normalize_financial_value(".76%")
    year = normalize_financial_value("2016")
    unavailable = normalize_financial_value("-")
    conflicting_sign = normalize_financial_value("(-1)")

    assert (
        leading_decimal.status,
        leading_decimal.numeric_token,
        leading_decimal.percent_marker,
    ) == (
        "recognized",
        ".76",
        True,
    )
    assert year.status == "ambiguous_date_or_year"
    assert unavailable.status == "unavailable"
    assert conflicting_sign.status == "ambiguous"


def test_parse_finqa_program_supports_observed_extended_syntax() -> None:
    result = parse_finqa_program(
        "table_average(beginning balance, none), multiply(.76, const_m1), divide(#0, 10379)"
    )

    assert result.is_valid
    assert [step.operation for step in result.steps] == ["table_average", "multiply", "divide"]
    assert result.steps[0].argument_kinds == ("table_label", "none")
    assert result.steps[1].argument_kinds == ("numeric_literal", "named_constant")
    assert result.steps[2].argument_kinds == ("intermediate_reference", "numeric_literal")


def test_parse_finqa_program_rejects_wrong_table_grammar_and_unknown_operations() -> None:
    wrong_table_argument = parse_finqa_program("table_sum(revenue, total)")
    unknown_operation = parse_finqa_program("mean(1, 2)")

    assert not wrong_table_argument.is_valid
    assert "unsupported table arguments" in wrong_table_argument.error
    assert not unknown_operation.is_valid
    assert "unsupported operation" in unknown_operation.error


def test_parse_finqa_program_supports_observed_numeric_table_sum_arguments() -> None:
    result = parse_finqa_program("table_sum(17695228, 963202), add(#0, 155213)")

    assert result.is_valid
    assert result.steps[0].argument_kinds == ("numeric_literal", "numeric_literal")


def test_build_structured_input_and_serialization_exclude_annotations() -> None:
    record = {
        "id": "example-1",
        "table": [["period", "value"], ["2020", "$ 2"]],
        "pre_text": ["before"],
        "post_text": ["after"],
        "qa": {
            "question": "What is the value?",
            "answer": "__FORBIDDEN_SENTINEL__",
            "exe_ans": 2.0,
            "program": "divide(2, 1)",
            "program_re": "divide(2, 1)",
            "steps": [],
            "gold_inds": {"table_1": "gold"},
            "ann_table_rows": [],
            "ann_text_rows": [],
            "explanation": "",
            "model_input": [["table_1", "gold"]],
            "tfidftopn": {"table_1": "gold"},
        },
        "table_retrieved": [{"ind": "table_1"}],
        "text_retrieved": [{"ind": "text_0"}],
    }

    structured = build_structured_input(record)
    serialized = serialize_table_for_retrieval(record["table"])

    assert set(structured) == {"id", "question", "table", "pre_text", "post_text"}
    assert not (set(structured) & FORBIDDEN_INFERENCE_FIELDS)
    assert "__FORBIDDEN_SENTINEL__" not in json.dumps(structured)
    assert "header | period | value" in serialized
    assert "row_1 | period: 2020 | value: $ 2" in serialized
    assert "gold" not in serialized
    assert_inference_safe(structured)


def test_inference_safety_rejects_extra_or_forbidden_fields() -> None:
    with pytest.raises(ValueError, match="disallowed fields"):
        assert_inference_safe({"id": "example", "answer": "leak"})


def test_annotation_audit_flags_evidence_without_dropping_empty_optional_fields() -> None:
    record = {
        "id": "example-1",
        "table": [["header"], ["row"]],
        "pre_text": ["source"],
        "post_text": [],
        "qa": {
            "gold_inds": {"text_-1": "source"},
            "program": "divide(.76, const_m1)",
            "answer": "",
            "explanation": "",
        },
    }

    diagnostic = audit_record_annotations(record)

    assert diagnostic.record_id == "example-1"
    assert diagnostic.invalid_evidence_count == 1
    assert diagnostic.program_parse.is_valid
    assert diagnostic.answer_is_empty
    assert diagnostic.explanation_is_empty


def test_display_answer_parser_keeps_currency_units_and_dates_as_text() -> None:
    numeric = parse_display_answer("-1,250.50%")
    currency = parse_display_answer("$ 13 million")
    date = parse_display_answer("December 31, 2019")

    assert (numeric.kind, numeric.numeric_value, numeric.is_percent) == (
        "numeric",
        -1250.50,
        True,
    )
    assert currency.kind == "text"
    assert date.kind == "text"


def test_display_answer_comparator_accepts_numeric_tolerance_boundary() -> None:
    within = compare_display_answers("100.0100", "100")
    beyond = compare_display_answers("100.0101", "100")

    assert within.status is ComparisonStatus.CORRECT
    assert beyond.status is ComparisonStatus.INCORRECT


def test_display_answer_comparator_requires_matching_percentage_status() -> None:
    result = compare_display_answers("0.53", "0.53%")

    assert result.status is ComparisonStatus.INCORRECT
    assert result.reason == "percentage marker mismatch"


def test_display_answer_comparator_normalizes_text_without_numeric_coercion() -> None:
    yes = compare_display_answers(" YES ", "yes")
    currency = compare_display_answers("13", "$ 13")

    assert yes.status is ComparisonStatus.CORRECT
    assert currency.status is ComparisonStatus.INCORRECT


def test_display_answer_comparator_reports_unavailable_and_unsupported_cases() -> None:
    unavailable = compare_display_answers("100", "")
    unsupported = compare_display_answers(None, "100")

    assert unavailable.status is ComparisonStatus.UNAVAILABLE_REFERENCE
    assert not unavailable.is_metric_eligible
    assert unsupported.status is ComparisonStatus.UNSUPPORTED_PREDICTION
    assert unsupported.is_metric_eligible


def test_reasoning_operations_and_provenance() -> None:
    left = NumericCandidate("8", 8, "table_1", "left", None, False, None)
    right = NumericCandidate("2", 2, "table_2", "right", None, False, None)

    assert reason_over_candidates("what is the total of these values?", [left, right]).result == 10
    assert reason_over_candidates("what is the difference?", [left, right]).result == 6
    assert reason_over_candidates("what is the product?", [left, right]).result == 16
    trace = reason_over_candidates("what is the ratio?", [left, right])
    assert trace.result == 4
    assert trace.evidence_references == ("table_1", "table_2")


def test_reasoning_abstains_for_zero_denominator_and_insufficient_operands() -> None:
    left = NumericCandidate("8", 8, "text_0", "left", None, False, None)
    zero = NumericCandidate("0", 0, "text_1", "right", None, False, None)

    assert (
        reason_over_candidates("what is the ratio?", [left, zero]).abstention_reason
        == "zero denominator"
    )
    assert reason_over_candidates("what is the total?", [left]).abstention_reason == (
        "insufficient safely parsed operands"
    )


def test_numeric_candidate_parsing_preserves_unsupported_and_parenthetical_negative() -> None:
    negative = parse_numeric_candidate("(1,250)", source_id="table_1", context="amount")
    percent = parse_numeric_candidate("12.5%", source_id="table_2", context="rate")
    currency = parse_numeric_candidate("$ 3.2", source_id="table_3", context="amount")
    scale = parse_numeric_candidate("3 million", source_id="table_4", context="amount")
    date = parse_numeric_candidate("2016", source_id="table_5", context="period")

    assert negative.value == -1250
    assert percent.value == 12.5 and percent.is_percent
    assert currency.value == Decimal("3.2") and currency.currency_symbol == "$"
    assert scale.value is None and scale.parse_reason == "scale conversion is unsupported"
    assert date.value is None and date.parse_reason == "ambiguous_date_or_year"


def test_reasoning_abstains_for_mismatched_metadata_and_ambiguous_intent() -> None:
    dollars = NumericCandidate("$ 2", 2, "table_1", "amount", "$", False, None)
    percent = NumericCandidate("5%", 5, "table_2", "rate", None, True, None)

    assert reason_over_candidates("what is the total?", [dollars, percent]).abstention_reason == (
        "mismatched unit or period metadata"
    )
    assert classify_intent("what is the change as a percentage?").intent is Intent.AMBIGUOUS
    assert classify_intent("what is the ratio?").operation is Operation.DIVIDE


def test_official_str_to_num_handles_percent_constants_and_commas() -> None:
    assert official_str_to_num("1,250") == 1250.0
    assert official_str_to_num("12.5%") == 0.125
    assert official_str_to_num("const_100") == 100.0
    assert official_str_to_num("const_m1") == -1.0
    assert official_str_to_num("n/a") is None


def test_execute_program_chains_steps_and_rounds_like_official_evaluator() -> None:
    result = execute_program("subtract(120, 100), divide(#0, 100)", [])
    assert result.is_valid and result.value == 0.2
    assert execute_program("divide(1, 3)", []).value == 0.33333
    assert execute_program("multiply(5%, const_100)", []).value == 5.0
    assert execute_program("greater(3, 2)", []).value == "yes"


def test_execute_program_runs_table_operations_by_row_label() -> None:
    table = [["", "2019", "2018"], ["revenue", "$ 10", "$ 20 ( 5 )"], ["note", "n/a", "x"]]
    assert execute_program("table_sum(revenue, none)", table).value == 30.0
    assert execute_program("table_average(revenue, none)", table).value == 15.0
    assert execute_program("table_max(missing, none)", table).error.startswith("table row")
    assert execute_program("table_min(note, none)", table).error.startswith("non-numeric")


def test_execute_program_reports_invalid_programs_without_raising() -> None:
    assert not execute_program("divide(1, 0)", []).is_valid
    assert not execute_program("add(#3, 1)", []).is_valid
    assert not execute_program("__import__(os)", []).is_valid
    assert not execute_program("add(greater(1, 2), 1)", []).is_valid


def test_compare_execution_uses_exact_equality_after_five_decimal_rounding() -> None:
    assert compare_execution(0.141234, 0.14123).is_correct
    assert not compare_execution(0.1412, 0.14123).is_correct
    assert compare_execution("yes", "yes").is_correct
    missing = compare_execution(None, 1.0)
    assert missing.status is ComparisonStatus.UNSUPPORTED_PREDICTION and not missing.is_correct


def test_gold_recall_at_k_reports_any_and_all_hits() -> None:
    recall = gold_recall_at_k(["table_1", "text_3", "text_0"], {"text_3", "table_2"}, 2)
    assert recall.any_gold and not recall.all_gold and recall.gold_count == 2
    with pytest.raises(ValueError):
        gold_recall_at_k(["table_1"], set(), 1)


def _segment_record() -> dict:
    return {
        "id": "X/2020/page_1.pdf-1",
        "pre_text": ["revenue grew 12.5% to $ 1,250 million in 2020 ."],
        "post_text": ["no other changes ."],
        "table": [["", "2020", "2019"], ["revenue", "$ 1250", "( 100 )"]],
        "qa": {"question": "what was the change?", "answer": "SENTINEL", "gold_inds": {}},
    }


def test_build_evidence_segments_uses_gold_key_convention_and_no_annotations() -> None:
    segments = build_evidence_segments(_segment_record())

    assert [s.key for s in segments] == ["table_1", "text_0", "text_1"]
    assert segments[0].text == "revenue | $ 1250 | ( 100 )"
    assert segments[0].header == ("", "2020", "2019")
    assert all("SENTINEL" not in s.text for s in segments)
    with_header = build_evidence_segments(_segment_record(), include_header_row=True)
    assert with_header[0].key == "table_0" and with_header[1].key == "table_1"


def test_segment_numeric_candidates_skip_row_label_and_keep_provenance() -> None:
    table_row, sentence, _ = build_evidence_segments(_segment_record())

    table_values = segment_numeric_candidates(table_row)
    assert [c.raw_value for c in table_values] == ["$ 1250", "( 100 )"]
    assert table_values[1].value == -100 and table_values[0].source_id == "table_1"
    text_values = segment_numeric_candidates(sentence)
    assert [c.raw_value for c in text_values] == ["12.5%", "1,250", "2020"]
    assert text_values[0].is_percent and text_values[2].value is None


def test_compare_programs_accepts_commutative_and_restructured_equivalents() -> None:
    gold = "subtract(120, 100), divide(#0, 100)"
    assert compare_programs(gold, gold).equivalent
    assert compare_programs("add(5, 3), multiply(#0, 2)", "add(3, 5), multiply(2, #0)").equivalent
    assert compare_programs(
        "divide(120, 100), subtract(#0, 1)", "divide(120, 100), subtract(#0, 1)"
    ).equivalent
    assert compare_programs("table_max(revenue, none)", "table_max(revenue, none)").equivalent


def test_compare_programs_rejects_order_tokens_and_invalid_predictions() -> None:
    gold = "subtract(120, 100), divide(#0, 100)"
    assert not compare_programs("subtract(100, 120), divide(#0, 100)", gold).equivalent
    unknown = compare_programs("subtract(120, 99), divide(#0, 100)", gold)
    assert not unknown.equivalent and "not in gold" in unknown.reason
    # Tokens are matched verbatim, as in the official evaluator: 100 is not const_100.
    assert not compare_programs("multiply(5, const_100)", "multiply(5, 100)").equivalent
    assert not compare_programs("divide(#1, 100), subtract(120, 100)", gold).equivalent
    assert not compare_programs("table_min(revenue, none)", "table_max(revenue, none)").equivalent
    assert not compare_programs("not a program", gold).equivalent
    assert compare_programs(None, gold).reason == "prediction is unavailable"
    with pytest.raises(ValueError):
        compare_programs(gold, "broken(")


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_retriever_config_file_loads_and_model_dir_can_be_overridden() -> None:
    path = REPOSITORY_ROOT / "configs" / "retriever_bert_base.toml"
    config = load_retriever_config(path, environment={})
    assert config.pretrained_name == "bert-base-uncased"
    assert config.evaluation_split == "dev" and config.include_header_row
    assert config.model_dir == Path("models/retriever-bert-base-dev-v1")
    drive = load_retriever_config(path, environment={"FINEVIDENCE_MODEL_DIR": "/content/drive/x"})
    assert drive.model_dir == Path("/content/drive/x")


def test_retriever_config_rejects_test_split_and_invalid_values(tmp_path) -> None:
    text = (REPOSITORY_ROOT / "configs" / "retriever_bert_base.toml").read_text()
    for old, new in [
        ('evaluation_split = "dev"', 'evaluation_split = "test"'),
        ("negatives_per_positive = 3", "negatives_per_positive = 0"),
        ('negative_sampling = "random"', 'negative_sampling = "gold"'),
    ]:
        path = tmp_path / "bad.toml"
        path.write_text(text.replace(old, new))
        with pytest.raises(ValueError):
            load_retriever_config(path, environment={})


def _fake_opener(payload: bytes):
    calls = []

    def opener(url: str):
        calls.append(url)
        return io.BytesIO(payload)

    return opener, calls


def test_download_verifies_checksum_and_never_overwrites(tmp_path, monkeypatch) -> None:
    payload = b"[]"
    monkeypatch.setitem(acquisition.PINNED_SHA256, "dev", hashlib.sha256(payload).hexdigest())
    opener, calls = _fake_opener(payload)

    states = acquisition.download_finqa_splits(tmp_path, ["dev"], opener=opener)
    again = acquisition.download_finqa_splits(tmp_path, ["dev"], opener=opener)

    assert states == {"dev": "downloaded; verified"}
    assert again == {"dev": "existing; verified, not overwritten"}
    assert len(calls) == 1 and acquisition.FINQA_REVISION in calls[0]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["dev.json"]


def test_download_rejects_checksum_mismatch_without_leaving_files(tmp_path) -> None:
    opener, _ = _fake_opener(b"[]")
    with pytest.raises(ValueError, match="SHA-256"):
        acquisition.download_finqa_splits(tmp_path, ["train"], opener=opener)
    assert list(tmp_path.iterdir()) == []
    with pytest.raises(ValueError, match="unknown"):
        acquisition.download_finqa_splits(tmp_path, ["private_test"], opener=opener)
    assert acquisition.DEVELOPMENT_SPLITS == ("train", "dev")
