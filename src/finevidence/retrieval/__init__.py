"""Evidence segmentation and configuration for retrieval experiments."""

from .config import MODEL_DIR_ENVIRONMENT_VARIABLE, RetrieverConfig, load_retriever_config
from .segments import (
    TEXT_NUMBER_SPAN,
    EvidenceSegment,
    build_evidence_segments,
    segment_numeric_candidates,
)

__all__ = [
    "MODEL_DIR_ENVIRONMENT_VARIABLE",
    "RetrieverConfig",
    "TEXT_NUMBER_SPAN",
    "EvidenceSegment",
    "build_evidence_segments",
    "load_retriever_config",
    "segment_numeric_candidates",
]
