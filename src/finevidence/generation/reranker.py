"""Label-free features of beam candidates for a learned reranker (Notebook 23).

Features read only the candidates, their log-probabilities, the retrieved fact texts and the raw
table, never an annotation field. Labels are attached separately, by the evaluation code.
"""

from __future__ import annotations

from collections.abc import Sequence

from finevidence.data.annotations import parse_finqa_program
from finevidence.evaluation.grounding import operand_grounding
from finevidence.reasoning.executor import execute_program

FEATURE_NAMES = (
    "rank",
    "log_prob",
    "gap_to_top",
    "executes",
    "grounded",
    "beam_agreement",
    "sample_agreement",
    "steps",
    "uses_table",
    "uses_constant",
    "literals",
)


def _value(program: str | None, table: Sequence[Sequence[object]]) -> object | None:
    if not program:
        return None
    result = execute_program(program, table)
    return result.value if result.is_valid else None


def beam_features(
    beams: Sequence[str | None],
    beam_scores: Sequence[float],
    samples: Sequence[str | None],
    fact_texts: Sequence[str],
    table: Sequence[Sequence[object]],
) -> list[list[float]]:
    """One feature row per beam, in ``FEATURE_NAMES`` order."""
    if not beams or len(beams) != len(beam_scores) or not samples:
        raise ValueError("need beams with matching scores and at least one sample")
    beam_values = [_value(p, table) for p in beams]
    sample_values = [_value(p, table) for p in samples]
    rows = []
    for rank, (program, score, value) in enumerate(
        zip(beams, beam_scores, beam_values, strict=True)
    ):
        parsed = parse_finqa_program(program) if program else None
        steps = parsed.steps if parsed is not None and parsed.is_valid else ()
        grounding = operand_grounding(program, fact_texts) if program else None
        executes = value is not None

        def share(values: Sequence[object | None], value: object | None = value) -> float:
            if value is None:
                return 0.0
            return sum(other == value for other in values) / len(values)

        rows.append(
            [
                float(rank),
                float(score),
                float(score - beam_scores[0]),
                float(executes),
                float(grounding is not None and not grounding.ungrounded),
                share(beam_values),
                share(sample_values),
                float(len(steps)),
                float(any(step.operation.startswith("table_") for step in steps)),
                float(any(a.startswith("const_") for step in steps for a in step.arguments)),
                float(grounding.literals if grounding else 0),
            ]
        )
    return rows
