"""Operand grounding: do a generated program's numbers appear in its input facts?"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from finevidence.data.annotations import parse_finqa_program

_CONTEXT_NUMBER = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?|-?\.\d+")
_LITERAL = re.compile(r"-?(?:\d+(?:\.\d+)?|\.\d+)%?")


@dataclass(frozen=True)
class OperandGrounding:
    """Counts of numeric literals in a program and how many occur in the input facts."""

    literals: int
    grounded: int
    ungrounded: tuple[str, ...]


def _magnitudes(text: str) -> set[float]:
    return {round(abs(float(match.replace(",", ""))), 6) for match in _CONTEXT_NUMBER.findall(text)}


def operand_grounding(program: str, fact_texts: Sequence[str]) -> OperandGrounding | None:
    """Return grounding counts, or None if the program does not parse.

    Values are compared as absolute magnitudes rounded to six decimals, because FinQA programs
    often drop signs and accounting parentheses shown in the report. Constants (``const_n``)
    and intermediate references are not literals and are not counted.
    """
    parsed = parse_finqa_program(program)
    if not parsed.is_valid:
        return None
    available = set().union(set(), *(_magnitudes(text) for text in fact_texts))
    literals = [
        argument
        for step in parsed.steps
        if not step.operation.startswith("table_")
        for argument in step.arguments
        if _LITERAL.fullmatch(argument)
    ]
    ungrounded = tuple(
        literal
        for literal in literals
        if round(abs(float(literal.rstrip("%"))), 6) not in available
    )
    return OperandGrounding(len(literals), len(literals) - len(ungrounded), ungrounded)
