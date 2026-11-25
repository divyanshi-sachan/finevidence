"""Label-free confidence for abstention, and accuracy against coverage.

The confidence of an answer is the share of beam candidates that execute to the same value as the
chosen candidate. It reads only the candidates, the raw table and the chosen index, never a label.
A system abstains below a threshold; accuracy is then measured on the answered records only and
is always reported with its coverage.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from finevidence.reasoning.executor import execute_program


def candidate_agreement(
    candidates: Sequence[str], table: Sequence[Sequence[object]], chosen_index: int
) -> float:
    """Share of all candidates whose executed value equals the chosen candidate's (0 if invalid)."""
    if not candidates:
        raise ValueError("no candidates")
    values = [execute_program(program, table) for program in candidates]
    chosen = values[chosen_index]
    if not chosen.is_valid:
        return 0.0
    return sum(value.is_valid and value.value == chosen.value for value in values) / len(values)


@dataclass(frozen=True)
class CoveragePoint:
    threshold: float
    answered: int
    coverage: float
    accuracy: float


def coverage_curve(confidences: Sequence[float], correct: Sequence[bool]) -> list[CoveragePoint]:
    """Accuracy on answered records for each distinct confidence threshold (answer if >= it)."""
    if len(confidences) != len(correct) or not confidences:
        raise ValueError("confidences and correct must be non-empty and the same length")
    points = []
    for threshold in sorted(set(confidences), reverse=True):
        answered = [
            ok
            for confidence, ok in zip(confidences, correct, strict=True)
            if confidence >= threshold
        ]
        points.append(
            CoveragePoint(
                threshold,
                len(answered),
                len(answered) / len(correct),
                sum(answered) / len(answered),
            )
        )
    return points


def majority_vote(
    candidates: Sequence[str], table: Sequence[Sequence[object]]
) -> tuple[int, float]:
    """Self-consistency: index of the first candidate with the most common executed value, and
    that value's share of all candidates (0 and 0.0 when no candidate executes)."""
    if not candidates:
        raise ValueError("no candidates")
    values = [execute_program(program, table) for program in candidates]
    counts: dict[object, int] = {}
    first: dict[object, int] = {}
    for index, value in enumerate(values):
        if value.is_valid:
            counts[value.value] = counts.get(value.value, 0) + 1
            first.setdefault(value.value, index)
    if not counts:
        return 0, 0.0
    winner = max(counts, key=lambda key: (counts[key], -first[key]))
    return first[winner], counts[winner] / len(candidates)
