"""Choose among beam-search candidates using only the model's own inputs.

Notebook 13 found copy errors (a number off by a digit, a year used as a value) among the
generator's mistakes. This selector keeps beam order but skips candidates that do not execute
or that use a numeric literal absent from the input facts. It reads the question's facts and
raw table only, never an annotation field.
"""

from __future__ import annotations

from collections.abc import Sequence

from finevidence.evaluation.grounding import operand_grounding
from finevidence.reasoning.executor import execute_program


def is_grounded_and_executable(
    program: str, fact_texts: Sequence[str], table: Sequence[Sequence[object]]
) -> bool:
    """True if the program executes and every numeric literal occurs in the facts."""
    grounding = operand_grounding(program, fact_texts)
    if grounding is None or grounding.grounded != grounding.literals:
        return False
    return execute_program(program, table).is_valid


def select_grounded_candidate(
    candidates: Sequence[str], fact_texts: Sequence[str], table: Sequence[Sequence[object]]
) -> int:
    """Index of the first grounded, executable candidate in beam order, else 0."""
    if not candidates:
        raise ValueError("no candidates to select from")
    for index, program in enumerate(candidates):
        if is_grounded_and_executable(program, fact_texts, table):
            return index
    return 0
