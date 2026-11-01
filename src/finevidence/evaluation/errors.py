"""Rule-based categories for incorrect FinQA program predictions.

Each incorrect prediction gets exactly one primary category, checked in this priority order:

1. ``invalid_program``: the prediction did not parse or execute.
2. ``retrieval_miss``: at least one gold fact was absent from the generator's input facts.
3. ``scale_error``: the value is off by a power of ten (for example a percent shown as 53
   instead of 0.53, or millions versus thousands).
4. ``sign_error``: the value is the negative of the reference (often reversed subtraction).
5. ``near_miss``: within 1% of the reference but not equal after official rounding.
6. ``operation_error``: the sequence of operations differs from the gold program.
7. ``operand_error``: same operations as the gold program, different arguments.
8. ``other``: none of the above applies.

These are deterministic proxies, not causal labels. For ``operand_error`` a detail flags
whether a wrong literal sits in the same table row as a gold literal, which usually means a
neighbouring column, such as the wrong year.
"""

from __future__ import annotations

import re
from collections.abc import Collection, Sequence
from dataclasses import dataclass

from finevidence.data.annotations import parse_finqa_program

CATEGORIES = (
    "invalid_program",
    "retrieval_miss",
    "scale_error",
    "sign_error",
    "near_miss",
    "operation_error",
    "operand_error",
    "other",
)

_SCALE_FACTORS = (100.0, 1_000.0, 1_000_000.0, 0.01, 0.001, 0.000_001)
_NUMBER = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?|-?\.\d+")
_LITERAL = re.compile(r"-?(?:\d+(?:\.\d+)?|\.\d+)%?")


@dataclass(frozen=True)
class ErrorCategory:
    """One incorrect prediction's primary category and an optional operand detail."""

    primary: str
    operand_detail: str | None = None


def _close(left: float, right: float, relative: float = 1e-3) -> bool:
    return abs(left - right) <= relative * max(abs(left), abs(right))


def _operations(program: str) -> tuple[str, ...] | None:
    parsed = parse_finqa_program(program)
    if not parsed.is_valid:
        return None
    return tuple(step.operation for step in parsed.steps)


def _literal_magnitudes(program: str) -> set[float]:
    parsed = parse_finqa_program(program)
    if not parsed.is_valid:
        return set()
    return {
        round(abs(float(argument.rstrip("%"))), 6)
        for step in parsed.steps
        for argument in step.arguments
        if _LITERAL.fullmatch(argument)
    }


def _row_magnitudes(row: Sequence[object]) -> set[float]:
    found: set[float] = set()
    for cell in row:
        for match in _NUMBER.findall(str(cell)):
            found.add(round(abs(float(match.replace(",", ""))), 6))
    return found


def _operand_detail(
    predicted_program: str, gold_program: str, table: Sequence[Sequence[object]]
) -> str:
    gold = _literal_magnitudes(gold_program)
    wrong = _literal_magnitudes(predicted_program) - gold
    if not wrong:
        return "same_literals_different_order_or_constant"
    for row in table:
        values = _row_magnitudes(row)
        if values & gold and values & wrong:
            return "same_table_row_as_gold"
    return "other_value"


def categorize_error(
    *,
    predicted_program: str | None,
    predicted_value: float | str | None,
    reference_value: float | str,
    gold_program: str,
    gold_keys: Collection[str],
    input_keys: Collection[str],
    table: Sequence[Sequence[object]],
) -> ErrorCategory:
    """Assign one primary category to a prediction already known to be incorrect."""
    if predicted_program is None or predicted_value is None:
        return ErrorCategory("invalid_program")
    if not set(gold_keys) <= set(input_keys):
        return ErrorCategory("retrieval_miss")

    both_numeric = isinstance(predicted_value, float | int) and isinstance(
        reference_value, float | int
    )
    if both_numeric and predicted_value != 0 and reference_value != 0:
        ratio = predicted_value / reference_value
        if any(_close(ratio, factor) for factor in _SCALE_FACTORS):
            return ErrorCategory("scale_error")
        if _close(predicted_value, -reference_value):
            return ErrorCategory("sign_error")
        if _close(predicted_value, reference_value, relative=1e-2):
            return ErrorCategory("near_miss")

    predicted_operations = _operations(predicted_program)
    gold_operations = _operations(gold_program)
    if predicted_operations is None or gold_operations is None:
        return ErrorCategory("other")
    if predicted_operations != gold_operations:
        return ErrorCategory("operation_error")
    return ErrorCategory("operand_error", _operand_detail(predicted_program, gold_program, table))
