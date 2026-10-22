"""Evidence segmentation and configuration for retrieval experiments."""

from .config import MODEL_DIR_ENVIRONMENT_VARIABLE, RetrieverConfig, load_retriever_config
from .pairs import (
    RetrieverPair,
    build_ranking_pairs,
    build_training_pairs,
    rank_keys,
    sample_epoch_pairs,
    segment_retrieval_text,
)
from .segments import (
    TEXT_NUMBER_SPAN,
    EvidenceSegment,
    build_evidence_segments,
    segment_numeric_candidates,
)

__all__ = [
    "MODEL_DIR_ENVIRONMENT_VARIABLE",
    "RetrieverConfig",
    "RetrieverPair",
    "TEXT_NUMBER_SPAN",
    "EvidenceSegment",
    "build_evidence_segments",
    "build_ranking_pairs",
    "build_training_pairs",
    "load_retriever_config",
    "rank_keys",
    "sample_epoch_pairs",
    "segment_numeric_candidates",
    "segment_retrieval_text",
]
