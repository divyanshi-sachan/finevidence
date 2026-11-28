"""Rule-based selection over saved candidate programs (no learned parameters).

Each candidate passes four fixed checks in order, and the first failure is its rejection reason:

1. ``malformed``: missing, or does not parse as a FinQA program.
2. ``execution``: fails controlled execution against the raw table (including references to an
   intermediate step that does not exist yet).
3. ``ungrounded_literal``: a numeric literal does not occur in the retrieved facts.
4. ``table_row_not_in_facts``: a ``table_*`` step names a row label absent from the retrieved facts.

The survivor with the highest length-normalized log-probability is selected; ties keep the earlier
candidate. If nothing survives, the first candidate (the top beam) is kept. The rules were written
before any dev evaluation and read only the candidates, the retrieved fact texts and the raw table,
never an annotation field.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from finevidence.data.annotations import parse_finqa_program
from finevidence.evaluation.grounding import operand_grounding
from finevidence.reasoning.executor import execute_program

REJECTION_REASONS = ("malformed", "execution", "ungrounded_literal", "table_row_not_in_facts")


@dataclass(frozen=True)
class RuleSelection:
    index: int
    rejections: tuple[str | None, ...]
    fallback: bool


def rejection_reason(
    program: str | None, fact_texts: Sequence[str], table: Sequence[Sequence[object]]
) -> str | None:
    """The first rule ``program`` breaks, or None if it survives every rule."""
    if not program:
        return "malformed"
    parsed = parse_finqa_program(program)
    if not parsed.is_valid:
        return "malformed"
    if not execute_program(program, table).is_valid:
        return "execution"
    grounding = operand_grounding(program, fact_texts)
    if grounding is None or grounding.ungrounded:
        return "ungrounded_literal"
    facts = " ".join(fact_texts).lower()
    for step in parsed.steps:
        if step.operation.startswith("table_") and step.arguments[0].lower() not in facts:
            return "table_row_not_in_facts"
    return None


def select_by_rules(
    candidates: Sequence[str | None],
    scores: Sequence[float],
    fact_texts: Sequence[str],
    table: Sequence[Sequence[object]],
) -> RuleSelection:
    """Highest-scoring surviving candidate; the first candidate if none survives."""
    if not candidates or len(candidates) != len(scores):
        raise ValueError("candidates and scores must be non-empty and the same length")
    rejections = tuple(rejection_reason(p, fact_texts, table) for p in candidates)
    survivors = [i for i, reason in enumerate(rejections) if reason is None]
    if not survivors:
        return RuleSelection(0, rejections, True)
    best = max(survivors, key=lambda i: (scores[i], -i))
    return RuleSelection(best, rejections, False)
