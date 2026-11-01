"""Evaluation helpers for FinEvidence experiments."""

from .answers import (
    AnswerComparisonResult,
    ComparisonStatus,
    ParsedDisplayAnswer,
    compare_display_answers,
    parse_display_answer,
)
from .errors import CATEGORIES, ErrorCategory, categorize_error
from .execution import ExecutionComparison, compare_execution
from .grounding import OperandGrounding, operand_grounding
from .program import ProgramComparison, compare_programs
from .retrieval import RetrievalRecall, gold_recall_at_k

__all__ = [
    "CATEGORIES",
    "AnswerComparisonResult",
    "ComparisonStatus",
    "ErrorCategory",
    "ExecutionComparison",
    "OperandGrounding",
    "ParsedDisplayAnswer",
    "ProgramComparison",
    "RetrievalRecall",
    "categorize_error",
    "compare_display_answers",
    "compare_execution",
    "compare_programs",
    "gold_recall_at_k",
    "operand_grounding",
    "parse_display_answer",
]
