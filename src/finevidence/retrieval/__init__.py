"""Evidence segmentation for retrieval experiments."""

from .segments import (
    TEXT_NUMBER_SPAN,
    EvidenceSegment,
    build_evidence_segments,
    segment_numeric_candidates,
)

__all__ = [
    "TEXT_NUMBER_SPAN",
    "EvidenceSegment",
    "build_evidence_segments",
    "segment_numeric_candidates",
]
