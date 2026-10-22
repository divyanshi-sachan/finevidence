"""Deterministic comparison for FinQA display-answer evaluation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

ABSOLUTE_TOLERANCE = Decimal("0.0001")
RELATIVE_TOLERANCE = Decimal("0.0001")

_NUMERIC_ANSWER = re.compile(
    r"^\s*(?P<sign>[+-])?(?P<number>(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+))(?P<percent>%?)\s*$"
)


class ComparisonStatus(StrEnum):
    """Outcome for one predicted display answer and one reference answer."""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    UNAVAILABLE_REFERENCE = "unavailable_reference"
    UNSUPPORTED_PREDICTION = "unsupported_prediction"


@dataclass(frozen=True)
class ParsedDisplayAnswer:
    """A display answer classified without coercing mixed surface forms."""

    raw: str
    normalized_text: str
    kind: str
    numeric_value: Decimal | None = None
    is_percent: bool = False


@dataclass(frozen=True)
class AnswerComparisonResult:
    """Structured answer-comparison result with a metric-eligibility signal."""

    status: ComparisonStatus
    reference: ParsedDisplayAnswer
    prediction: ParsedDisplayAnswer | None
    reason: str

    @property
    def is_metric_eligible(self) -> bool:
        """Whether this reference belongs in the display-answer denominator."""
        return self.status is not ComparisonStatus.UNAVAILABLE_REFERENCE


def parse_display_answer(value: str) -> ParsedDisplayAnswer:
    """Classify one raw display answer under the documented FinQA policy."""
    if not isinstance(value, str):
        raise TypeError("display answer must be a string")

    normalized_text = " ".join(value.strip().casefold().split())
    if not normalized_text:
        return ParsedDisplayAnswer(value, normalized_text, "empty")

    match = _NUMERIC_ANSWER.fullmatch(value)
    if match is None:
        return ParsedDisplayAnswer(value, normalized_text, "text")

    try:
        numeric_value = Decimal(match["number"].replace(",", ""))
    except InvalidOperation:
        return ParsedDisplayAnswer(value, normalized_text, "text")
    if match["sign"] == "-":
        numeric_value = -numeric_value
    return ParsedDisplayAnswer(
        raw=value,
        normalized_text=normalized_text,
        kind="numeric",
        numeric_value=numeric_value,
        is_percent=bool(match["percent"]),
    )


def compare_display_answers(prediction: str | None, reference: str) -> AnswerComparisonResult:
    """Compare prediction and reference without using executable-answer annotations."""
    parsed_reference = parse_display_answer(reference)
    if parsed_reference.kind == "empty":
        return AnswerComparisonResult(
            ComparisonStatus.UNAVAILABLE_REFERENCE,
            parsed_reference,
            None,
            "reference display answer is empty",
        )
    if prediction is None:
        return AnswerComparisonResult(
            ComparisonStatus.UNSUPPORTED_PREDICTION,
            parsed_reference,
            None,
            "prediction is unavailable",
        )

    parsed_prediction = parse_display_answer(prediction)
    if parsed_prediction.kind == "empty":
        return AnswerComparisonResult(
            ComparisonStatus.UNSUPPORTED_PREDICTION,
            parsed_reference,
            parsed_prediction,
            "prediction is empty",
        )

    if parsed_reference.kind == "numeric" and parsed_prediction.kind == "numeric":
        if parsed_reference.is_percent != parsed_prediction.is_percent:
            return AnswerComparisonResult(
                ComparisonStatus.INCORRECT,
                parsed_reference,
                parsed_prediction,
                "percentage marker mismatch",
            )
        tolerance = max(
            ABSOLUTE_TOLERANCE,
            RELATIVE_TOLERANCE * max(abs(parsed_reference.numeric_value), Decimal("1")),
        )
        if abs(parsed_prediction.numeric_value - parsed_reference.numeric_value) <= tolerance:
            return AnswerComparisonResult(
                ComparisonStatus.CORRECT,
                parsed_reference,
                parsed_prediction,
                "numeric values match within tolerance",
            )
        return AnswerComparisonResult(
            ComparisonStatus.INCORRECT,
            parsed_reference,
            parsed_prediction,
            "numeric values differ beyond tolerance",
        )

    if parsed_reference.kind != parsed_prediction.kind:
        return AnswerComparisonResult(
            ComparisonStatus.INCORRECT,
            parsed_reference,
            parsed_prediction,
            "numeric and text answer types differ",
        )
    if parsed_reference.normalized_text == parsed_prediction.normalized_text:
        return AnswerComparisonResult(
            ComparisonStatus.CORRECT,
            parsed_reference,
            parsed_prediction,
            "normalized text matches exactly",
        )
    return AnswerComparisonResult(
        ComparisonStatus.INCORRECT,
        parsed_reference,
        parsed_prediction,
        "normalized text differs",
    )
