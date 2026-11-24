import pytest

from finevidence.generation.causal import (
    IGNORE_INDEX,
    PROGRAM_MARKER,
    build_causal_example,
    causal_prompt,
    extract_program,
)


def test_prompt_ends_with_program_marker():
    prompt = causal_prompt("question: q? facts: [1] a")
    assert prompt.endswith(PROGRAM_MARKER) and "question: q?" in prompt


def test_only_target_and_eos_are_trained():
    input_ids, labels = build_causal_example([1, 2, 3], [9], [7, 8], eos_id=0, max_source_tokens=10)
    assert input_ids == [1, 2, 3, 9, 7, 8, 0]
    assert labels == [IGNORE_INDEX] * 4 + [7, 8, 0]


def test_source_is_truncated_from_the_end_and_marker_kept():
    input_ids, labels = build_causal_example([1, 2, 3, 4], [9], [7], eos_id=0, max_source_tokens=2)
    assert input_ids == [1, 2, 9, 7, 0]
    assert labels.count(IGNORE_INDEX) == 3
    with pytest.raises(ValueError):
        build_causal_example([1], [9], [7], eos_id=0, max_source_tokens=0)


def test_extract_program_stops_at_first_line():
    assert extract_program(" divide(1, 2)\nquestion: more") == "divide(1, 2)"
