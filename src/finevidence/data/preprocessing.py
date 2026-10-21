"""Reversible preprocessing helpers for FinQA raw records."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .annotations import (
    EvidenceReference,
    ProgramParseResult,
    parse_finqa_program,
    validate_evidence_key,
)

INFERENCE_INPUT_FIELDS = frozenset({"id", "question", "table", "pre_text", "post_text"})
FORBIDDEN_INFERENCE_FIELDS = frozenset(
    {
        "answer",
        "exe_ans",
        "program",
        "program_re",
        "steps",
        "gold_inds",
        "ann_table_rows",
        "ann_text_rows",
        "explanation",
        "table_retrieved",
        "text_retrieved",
        "table_retrieved_all",
        "text_retrieved_all",
        "model_input",
        "tfidftopn",
    }
)

_UNAVAILABLE_MARKERS = frozenset({"", "-", "—", "–", "n/a", "na", "none", "not available"})
_SCALE_PATTERN = r"(?P<scale>thousand|thousands|million|millions|billion|billions)"
_VALUE_PATTERN = re.compile(
    r"^\s*(?P<open>\()?\s*(?P<currency>[$€£])?\s*(?P<sign>[+-])?\s*"
    r"(?P<number>(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+))\s*(?P<percent>%?)\s*(?P<close>\))?\s*"
    rf"(?:{_SCALE_PATTERN})?\s*$",
    re.IGNORECASE,
)
_YEAR_PATTERN = re.compile(r"^(?:19|20)\d{2}$")
_DATE_PATTERN = re.compile(
    r"^(?:january|february|march|april|may|june|july|august|september|october|november|december)"
    r"\s+\d{1,2}(?:,?\s+\d{4})?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class FinancialValueCandidate:
    """A reversible, non-executing reading of one raw financial surface string."""

    raw: str
    status: str
    numeric_token: str | None = None
    sign_style: str | None = None
    currency_symbol: str | None = None
    percent_marker: bool = False
    scale_word: str | None = None
    local_context: str | None = None


@dataclass(frozen=True)
class RecordAnnotationDiagnostic:
    """Annotation-quality signals that preserve the record and raw labels."""

    record_id: str
    evidence_references: tuple[EvidenceReference, ...]
    program_parse: ProgramParseResult
    answer_is_empty: bool
    explanation_is_empty: bool

    @property
    def invalid_evidence_count(self) -> int:
        return sum(not reference.is_valid for reference in self.evidence_references)


def normalize_financial_value(
    raw: str, *, local_context: str | None = None
) -> FinancialValueCandidate:
    """Return a reversible candidate without inferring a scalar value or units."""
    if not isinstance(raw, str):
        raise TypeError("raw must be a string")

    stripped = raw.strip()
    if stripped.lower() in _UNAVAILABLE_MARKERS:
        return FinancialValueCandidate(raw=raw, status="unavailable", local_context=local_context)
    if _YEAR_PATTERN.fullmatch(stripped) or _DATE_PATTERN.fullmatch(stripped):
        return FinancialValueCandidate(
            raw=raw, status="ambiguous_date_or_year", local_context=local_context
        )
    if stripped.lower() in {"thousand", "thousands", "million", "millions", "billion", "billions"}:
        return FinancialValueCandidate(
            raw=raw, status="ambiguous_scale_only", local_context=local_context
        )

    match = _VALUE_PATTERN.fullmatch(raw)
    if match is None:
        return FinancialValueCandidate(raw=raw, status="unsupported", local_context=local_context)

    opening_parenthesis = match["open"]
    closing_parenthesis = match["close"]
    explicit_sign = match["sign"]
    if bool(opening_parenthesis) != bool(closing_parenthesis) or (
        opening_parenthesis and explicit_sign
    ):
        return FinancialValueCandidate(raw=raw, status="ambiguous", local_context=local_context)

    sign_style = (
        "accounting_parentheses"
        if opening_parenthesis
        else "explicit_sign"
        if explicit_sign
        else "unsigned"
    )
    return FinancialValueCandidate(
        raw=raw,
        status="recognized",
        numeric_token=match["number"],
        sign_style=sign_style,
        currency_symbol=match["currency"],
        percent_marker=bool(match["percent"]),
        scale_word=match["scale"].lower() if match["scale"] else None,
        local_context=local_context,
    )


def build_structured_input(record: Mapping[str, Any]) -> dict[str, Any]:
    """Build the allowlisted structured input for an answer-prediction task."""
    qa = _required_mapping(record, "qa")
    return {
        "id": _required_string(record, "id"),
        "question": _required_string(qa, "question"),
        "table": _required_list(record, "table"),
        "pre_text": _required_list(record, "pre_text"),
        "post_text": _required_list(record, "post_text"),
    }


def serialize_table_for_retrieval(table: Sequence[Sequence[Any]]) -> str:
    """Render raw table cells with explicit header and row boundaries.

    The representation is deterministic and preserves cell text. It does not use
    answers, evidence, or publisher-provided retrieval artifacts.
    """
    if not table:
        raise ValueError("table must contain at least one row")
    header = [str(cell) for cell in table[0]]
    if not header:
        raise ValueError("table header must contain at least one cell")

    lines = ["header | " + " | ".join(header)]
    for row_index, row in enumerate(table[1:], start=1):
        if len(row) != len(header):
            raise ValueError("table row width differs from header width")
        associations = [f"{column}: {value}" for column, value in zip(header, row, strict=True)]
        lines.append(f"row_{row_index} | " + " | ".join(associations))
    return "\n".join(lines)


def assert_inference_safe(payload: Mapping[str, Any]) -> None:
    """Raise if a structured payload has a non-allowlisted field."""
    unexpected = set(payload) - INFERENCE_INPUT_FIELDS
    forbidden = set(payload) & FORBIDDEN_INFERENCE_FIELDS
    if unexpected or forbidden:
        raise ValueError(
            f"inference payload contains disallowed fields: {sorted(unexpected | forbidden)}"
        )


def audit_record_annotations(record: Mapping[str, Any]) -> RecordAnnotationDiagnostic:
    """Inspect raw annotations without changing, dropping, or executing them."""
    qa = _required_mapping(record, "qa")
    pre_text = _required_list(record, "pre_text")
    post_text = _required_list(record, "post_text")
    table = _required_list(record, "table")
    gold_indices = _required_mapping(qa, "gold_inds")
    references = tuple(
        validate_evidence_key(
            str(raw_key), text_count=len(pre_text) + len(post_text), table_count=len(table)
        )
        for raw_key in gold_indices
    )
    return RecordAnnotationDiagnostic(
        record_id=_required_string(record, "id"),
        evidence_references=references,
        program_parse=parse_finqa_program(_required_string(qa, "program")),
        answer_is_empty=not _required_string(qa, "answer").strip(),
        explanation_is_empty=not _required_string(qa, "explanation").strip(),
    )


def _required_mapping(record: Mapping[str, Any], field: str) -> Mapping[str, Any]:
    value = record.get(field)
    if not isinstance(value, Mapping):
        raise ValueError(f"{field!r} must be a mapping")
    return value


def _required_string(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str):
        raise ValueError(f"{field!r} must be a string")
    return value


def _required_list(record: Mapping[str, Any], field: str) -> list[Any]:
    value = record.get(field)
    if not isinstance(value, list):
        raise ValueError(f"{field!r} must be a list")
    return value
