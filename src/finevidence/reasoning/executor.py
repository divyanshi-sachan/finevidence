"""Safe execution of FinQA-style programs, mirroring the official evaluator's semantics.

The official script (``code/evaluate/evaluate.py`` at the pinned FinQA commit) executes a
predicted program with Python floats, rounds a numeric final result to five decimals, and
compares it for exact equality with ``exe_ans``. This module reproduces those value rules on
top of the non-executing parser; it never calls ``eval`` or ``exec``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from finevidence.data.annotations import parse_finqa_program
from finevidence.evaluation.execution import OFFICIAL_ROUNDING_DECIMALS

ExecutionValue = float | str


@dataclass(frozen=True)
class ExecutionResult:
    """A final program value, or the reason execution was invalid."""

    value: ExecutionValue | None
    error: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.error is None


def official_str_to_num(text: str) -> float | None:
    """Convert one program or table token as the official evaluator does, or return None."""
    text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        pass
    if "%" in text:
        try:
            return float(text.replace("%", "")) / 100.0
        except ValueError:
            return None
    if text.startswith("const_"):
        constant = text.removeprefix("const_")
        try:
            return -1.0 if constant == "m1" else float(constant)
        except ValueError:
            return None
    return None


def _table_row_values(row: Sequence[object]) -> list[float] | None:
    values = []
    for cell in row:
        token = str(cell).replace("$", "").strip().split("(")[0].strip()
        number = official_str_to_num(token)
        if number is None:
            return None
        values.append(number)
    return values


def execute_program(program: str, table: Sequence[Sequence[object]]) -> ExecutionResult:
    """Execute a FinQA program string against its raw table under official semantics."""
    parsed = parse_finqa_program(program)
    if not parsed.is_valid:
        return ExecutionResult(None, f"parse error: {parsed.error}")

    # The official evaluator keys rows by their first cell; a later duplicate label wins.
    rows_by_label = {str(row[0]): row[1:] for row in table if row}
    results: list[ExecutionValue] = []
    for step in parsed.steps:
        if step.operation.startswith("table_"):
            label = step.arguments[0]
            if label not in rows_by_label:
                return ExecutionResult(None, f"table row not found: {label!r}")
            values = _table_row_values(rows_by_label[label])
            if not values:
                return ExecutionResult(None, f"non-numeric table row: {label!r}")
            aggregate = {
                "table_max": max,
                "table_min": min,
                "table_sum": sum,
                "table_average": lambda items: sum(items) / len(items),
            }[step.operation]
            results.append(aggregate(values))
            continue

        operands: list[float] = []
        for argument in step.arguments:
            if argument.startswith("#"):
                index = int(argument[1:])
                if index >= len(results) or isinstance(results[index], str):
                    return ExecutionResult(None, f"invalid intermediate reference: {argument}")
                operands.append(results[index])
            else:
                number = official_str_to_num(argument)
                if number is None:
                    return ExecutionResult(None, f"non-numeric argument: {argument!r}")
                operands.append(number)
        left, right = operands
        try:
            if step.operation == "add":
                results.append(left + right)
            elif step.operation == "subtract":
                results.append(left - right)
            elif step.operation == "multiply":
                results.append(left * right)
            elif step.operation == "divide":
                results.append(left / right)
            elif step.operation == "exp":
                results.append(left**right)
            elif step.operation == "greater":
                results.append("yes" if left > right else "no")
        except (ZeroDivisionError, OverflowError) as error:
            return ExecutionResult(None, f"arithmetic error: {error}")

    final = results[-1]
    if isinstance(final, str):
        return ExecutionResult(final)
    if isinstance(final, complex):
        return ExecutionResult(None, "complex result")
    return ExecutionResult(round(final, OFFICIAL_ROUNDING_DECIMALS))
