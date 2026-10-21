"""Dataset loading, validation, and reversible preprocessing helpers."""

from .annotations import SUPPORTED_OPERATIONS, parse_finqa_program, validate_evidence_key
from .finqa import load_finqa_split
from .preprocessing import (
    FORBIDDEN_INFERENCE_FIELDS,
    INFERENCE_INPUT_FIELDS,
    FinancialValueCandidate,
    RecordAnnotationDiagnostic,
    assert_inference_safe,
    audit_record_annotations,
    build_structured_input,
    normalize_financial_value,
    serialize_table_for_retrieval,
)
from .validation import validate_records

__all__ = [
    "FORBIDDEN_INFERENCE_FIELDS",
    "INFERENCE_INPUT_FIELDS",
    "SUPPORTED_OPERATIONS",
    "FinancialValueCandidate",
    "RecordAnnotationDiagnostic",
    "assert_inference_safe",
    "audit_record_annotations",
    "build_structured_input",
    "load_finqa_split",
    "normalize_financial_value",
    "parse_finqa_program",
    "serialize_table_for_retrieval",
    "validate_evidence_key",
    "validate_records",
]
