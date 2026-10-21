"""Small, deterministic arithmetic over explicitly grounded numeric candidates."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from finevidence.data.preprocessing import normalize_financial_value


class Intent(StrEnum):
    ADDITIVE = "additive"
    SUBTRACTIVE = "subtractive"
    MULTIPLICATIVE = "multiplicative"
    DIVISIVE = "divisive"
    COMPARISON = "comparison"
    AMBIGUOUS = "ambiguous"


class Operation(StrEnum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


@dataclass(frozen=True)
class NumericCandidate:
    """One safely parsed source value; raw text remains authoritative."""

    raw_value: str
    value: Decimal | None
    source_id: str
    context: str
    currency_symbol: str | None
    is_percent: bool
    scale_word: str | None
    period: str | None = None
    parse_reason: str | None = None


@dataclass(frozen=True)
class OperationHypothesis:
    """A question-derived operation proposal, separate from operand selection."""

    intent: Intent
    operation: Operation | None
    rationale: str
    ambiguous: bool = False


@dataclass(frozen=True)
class ReasoningTrace:
    """A calculation record or a conservative abstention."""

    hypothesis: OperationHypothesis
    operands: tuple[NumericCandidate, ...]
    result: Decimal | None
    evidence_references: tuple[str, ...]
    abstention_reason: str | None = None

    @property
    def answered(self) -> bool:
        return self.result is not None


_PATTERNS: tuple[tuple[Intent, Operation | None, re.Pattern[str], str], ...] = (
    (
        Intent.SUBTRACTIVE,
        Operation.SUBTRACT,
        re.compile(r"\b(change|difference|increase|decrease)\b", re.I),
        "difference/change cue",
    ),
    (
        Intent.DIVISIVE,
        Operation.DIVIDE,
        re.compile(r"\b(ratio|proportion|percentage|what percent)\b", re.I),
        "ratio/percentage cue",
    ),
    (
        Intent.MULTIPLICATIVE,
        Operation.MULTIPLY,
        re.compile(r"\b(times|product)\b", re.I),
        "multiplication cue",
    ),
    (
        Intent.ADDITIVE,
        Operation.ADD,
        re.compile(r"\b(sum|combined|total)\b", re.I),
        "sum/total cue",
    ),
    (
        Intent.COMPARISON,
        None,
        re.compile(r"\b(compare|versus|greater|less)\b", re.I),
        "comparison cue",
    ),
)


def classify_intent(question: str) -> OperationHypothesis:
    """Classify a small documented intent scope without inspecting annotations."""
    matches = [entry for entry in _PATTERNS if entry[2].search(question)]
    if len(matches) != 1:
        return OperationHypothesis(Intent.AMBIGUOUS, None, "zero or multiple supported cues", True)
    intent, operation, _, rationale = matches[0]
    return OperationHypothesis(intent, operation, rationale)


def parse_numeric_candidate(
    raw_value: str,
    *,
    source_id: str,
    context: str,
    period: str | None = None,
) -> NumericCandidate:
    """Safely parse an isolated value without currency, scale, or percent conversion."""
    normalized = normalize_financial_value(raw_value, local_context=context)
    if normalized.status != "recognized" or normalized.numeric_token is None:
        return NumericCandidate(
            raw_value, None, source_id, context, None, False, None, period, normalized.status
        )
    if normalized.scale_word is not None:
        return NumericCandidate(
            raw_value,
            None,
            source_id,
            context,
            normalized.currency_symbol,
            normalized.percent_marker,
            normalized.scale_word,
            period,
            "scale conversion is unsupported",
        )
    try:
        value = Decimal(normalized.numeric_token.replace(",", ""))
    except InvalidOperation:
        return NumericCandidate(
            raw_value,
            None,
            source_id,
            context,
            normalized.currency_symbol,
            normalized.percent_marker,
            normalized.scale_word,
            period,
            "invalid decimal token",
        )
    if normalized.sign_style == "accounting_parentheses":
        value = -value
    elif raw_value.strip().lstrip("($€£ ").startswith("-"):
        value = -value
    return NumericCandidate(
        raw_value,
        value,
        source_id,
        context,
        normalized.currency_symbol,
        normalized.percent_marker,
        normalized.scale_word,
        period,
    )


def reason_over_candidates(question: str, candidates: list[NumericCandidate]) -> ReasoningTrace:
    """Compute one operation over the first two compatible, grounded candidates."""
    hypothesis = classify_intent(question)
    if hypothesis.operation is None:
        return ReasoningTrace(hypothesis, (), None, (), "unsupported or ambiguous question intent")

    valid = [candidate for candidate in candidates if candidate.value is not None]
    if len(valid) < 2:
        return ReasoningTrace(
            hypothesis,
            tuple(valid),
            None,
            tuple(c.source_id for c in valid),
            "insufficient safely parsed operands",
        )
    left, right = valid[:2]
    if not _metadata_compatible(left, right):
        return ReasoningTrace(
            hypothesis,
            (left, right),
            None,
            (left.source_id, right.source_id),
            "mismatched unit or period metadata",
        )
    if hypothesis.operation is Operation.DIVIDE and right.value == 0:
        return ReasoningTrace(
            hypothesis, (left, right), None, (left.source_id, right.source_id), "zero denominator"
        )

    result = {
        Operation.ADD: left.value + right.value,
        Operation.SUBTRACT: left.value - right.value,
        Operation.MULTIPLY: left.value * right.value,
        Operation.DIVIDE: left.value / right.value,
    }[hypothesis.operation]
    return ReasoningTrace(hypothesis, (left, right), result, (left.source_id, right.source_id))


def _metadata_compatible(left: NumericCandidate, right: NumericCandidate) -> bool:
    return (
        left.currency_symbol == right.currency_symbol
        and left.is_percent == right.is_percent
        and left.scale_word == right.scale_word
        and (left.period is None or right.period is None or left.period == right.period)
    )
