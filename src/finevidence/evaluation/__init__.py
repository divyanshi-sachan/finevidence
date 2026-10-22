"""Evaluation helpers for FinEvidence experiments."""

from .answers import (
    AnswerComparisonResult,
    ComparisonStatus,
    ParsedDisplayAnswer,
    compare_display_answers,
    parse_display_answer,
)
from .execution import ExecutionComparison, compare_execution
from .grounding import OperandGrounding, operand_grounding
from .program import ProgramComparison, compare_programs
from .retrieval import RetrievalRecall, gold_recall_at_k

__all__ = [
    "AnswerComparisonResult",
    "ComparisonStatus",
    "ExecutionComparison",
    "OperandGrounding",
    "ParsedDisplayAnswer",
    "ProgramComparison",
    "RetrievalRecall",
    "compare_display_answers",
    "compare_execution",
    "compare_programs",
    "gold_recall_at_k",
    "operand_grounding",
    "parse_display_answer",
]
