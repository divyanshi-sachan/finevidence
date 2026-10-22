"""Score one generated program under the official execution and program conventions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from finevidence.evaluation.execution import compare_execution
from finevidence.evaluation.grounding import operand_grounding
from finevidence.evaluation.program import compare_programs
from finevidence.reasoning.executor import execute_program


@dataclass(frozen=True)
class ProgramPredictionScore:
    record_id: str
    prediction: str | None
    executed_value: float | str | None
    execution_correct: bool
    program_correct: bool
    valid: bool
    literals: int
    grounded_literals: int
    error: str | None


def score_program_prediction(
    record: Mapping[str, Any], prediction: str | None, fact_texts: Sequence[str]
) -> ProgramPredictionScore:
    """Execute against the record's raw table, then compare with ``exe_ans`` and ``program``.

    Annotations are read here only, after the prediction is fixed.
    """
    qa = record["qa"]
    if prediction is None:
        return ProgramPredictionScore(
            str(record["id"]), None, None, False, False, False, 0, 0, "no prediction"
        )
    executed = execute_program(prediction, record["table"])
    grounding = operand_grounding(prediction, fact_texts)
    return ProgramPredictionScore(
        record_id=str(record["id"]),
        prediction=prediction,
        executed_value=executed.value,
        execution_correct=compare_execution(executed.value, qa["exe_ans"]).is_correct,
        program_correct=compare_programs(prediction, qa["program"]).equivalent,
        valid=executed.is_valid,
        literals=grounding.literals if grounding else 0,
        grounded_literals=grounding.grounded if grounding else 0,
        error=executed.error,
    )


def summarize_scores(scores: Iterable[ProgramPredictionScore]) -> dict[str, float | int]:
    """Official-style rates over all records: invalid programs count as incorrect."""
    scores = list(scores)
    if not scores:
        raise ValueError("no scores to summarize")
    total = len(scores)
    literals = sum(score.literals for score in scores)
    return {
        "records": total,
        "execution_correct": sum(score.execution_correct for score in scores),
        "execution_accuracy": round(sum(score.execution_correct for score in scores) / total, 6),
        "program_accuracy": round(sum(score.program_correct for score in scores) / total, 6),
        "invalid_rate": round(sum(not score.valid for score in scores) / total, 6),
        "operand_grounding_rate": round(
            sum(score.grounded_literals for score in scores) / literals, 6
        )
        if literals
        else 0.0,
    }
