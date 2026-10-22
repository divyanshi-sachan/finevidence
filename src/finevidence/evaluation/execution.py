"""Execution accuracy under the official FinQA convention.

A prediction is correct only when its executed value equals the reference ``exe_ans``
exactly, after rounding a numeric prediction to five decimals. Every record stays in the
denominator; an invalid or missing prediction counts as incorrect, not as excluded.
"""

from __future__ import annotations

from dataclasses import dataclass

from .answers import ComparisonStatus

OFFICIAL_ROUNDING_DECIMALS = 5


@dataclass(frozen=True)
class ExecutionComparison:
    """One prediction compared against one ``exe_ans`` reference."""

    status: ComparisonStatus
    prediction: float | str | None
    reference: float | str
    reason: str

    @property
    def is_correct(self) -> bool:
        return self.status is ComparisonStatus.CORRECT


def _round_numeric(value: float | str) -> float | str:
    if isinstance(value, bool):
        raise TypeError("execution values must be float or yes/no strings, not bool")
    if isinstance(value, int | float):
        return round(float(value), OFFICIAL_ROUNDING_DECIMALS)
    return value


def compare_execution(
    prediction: float | str | None, reference: float | str
) -> ExecutionComparison:
    """Compare an executed prediction with ``exe_ans`` using official exact equality."""
    if prediction is None:
        return ExecutionComparison(
            ComparisonStatus.UNSUPPORTED_PREDICTION, None, reference, "prediction is unavailable"
        )
    rounded = _round_numeric(prediction)
    if rounded == reference:
        return ExecutionComparison(
            ComparisonStatus.CORRECT, rounded, reference, "executed value equals exe_ans"
        )
    return ExecutionComparison(
        ComparisonStatus.INCORRECT, rounded, reference, "executed value differs from exe_ans"
    )
