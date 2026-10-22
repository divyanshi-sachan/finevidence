"""Question-segment pairs for training and applying a cross-encoder evidence retriever.

Sampling follows the official FinQA retriever: every gold segment is a positive, every
other segment joins one global negative pool, and each epoch draws
``negatives_per_positive * len(positives)`` negatives from that pool afresh. One deliberate
difference: positives are rendered from the raw context by their ``gold_inds`` *key*, exactly
like negatives, instead of using the annotated ``gold_inds`` text. A shared rendering stops
the classifier from separating the classes by formatting alone.
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from finevidence.data.preprocessing import build_structured_input

from .segments import EvidenceSegment, build_evidence_segments


@dataclass(frozen=True)
class RetrieverPair:
    """One (question, segment) input; ``label`` is None at prediction time."""

    record_id: str
    key: str
    question: str
    text: str
    label: int | None = None


def segment_retrieval_text(segment: EvidenceSegment) -> str:
    """Render a segment for the retriever, pairing table cells with their column headers."""
    if segment.source == "text":
        return segment.text
    if segment.key == "table_0":
        return "header: " + " | ".join(segment.cells)
    label, *values = segment.cells
    columns = segment.header[1:]
    pairs = [f"{column}: {value}" for column, value in zip(columns, values, strict=False)]
    return " | ".join([f"row: {label}", *pairs])


def build_ranking_pairs(
    record: Mapping[str, Any], *, include_header_row: bool = True
) -> list[RetrieverPair]:
    """Unlabelled pairs for every segment of one record, built from allowlisted fields only."""
    source = build_structured_input(record)
    return [
        RetrieverPair(
            source["id"], segment.key, source["question"], segment_retrieval_text(segment)
        )
        for segment in build_evidence_segments(record, include_header_row=include_header_row)
    ]


def build_training_pairs(
    records: Iterable[Mapping[str, Any]], *, include_header_row: bool = True
) -> tuple[list[RetrieverPair], list[RetrieverPair], Counter[str]]:
    """Return labelled positives, the full negative pool, and counts of unmatched gold keys.

    Gold keys are read from ``qa.gold_inds`` only to assign labels. A gold key with no
    matching segment (such as the flagged ``text_-1``) is counted and left out, never repaired.
    """
    positives: list[RetrieverPair] = []
    negatives: list[RetrieverPair] = []
    unmatched: Counter[str] = Counter()
    for record in records:
        gold_keys = set(record["qa"]["gold_inds"])
        pairs = build_ranking_pairs(record, include_header_row=include_header_row)
        available = {pair.key for pair in pairs}
        for key in sorted(gold_keys - available):
            unmatched[key] += 1
        for pair in pairs:
            is_gold = pair.key in gold_keys
            labelled = RetrieverPair(
                pair.record_id, pair.key, pair.question, pair.text, int(is_gold)
            )
            (positives if is_gold else negatives).append(labelled)
    return positives, negatives, unmatched


def sample_epoch_pairs(
    positives: Sequence[RetrieverPair],
    negatives: Sequence[RetrieverPair],
    *,
    negatives_per_positive: int,
    seed: int,
    epoch: int,
) -> list[RetrieverPair]:
    """All positives plus a fresh, seeded negative sample for one epoch, shuffled."""
    rng = random.Random(seed * 1_000_003 + epoch)
    count = min(len(negatives), negatives_per_positive * len(positives))
    epoch_pairs = [*positives, *rng.sample(list(negatives), count)]
    rng.shuffle(epoch_pairs)
    return epoch_pairs


def rank_keys(keys: Sequence[str], scores: Sequence[float]) -> list[str]:
    """Order segment keys by descending score; ties keep segment order."""
    if len(keys) != len(scores):
        raise ValueError("keys and scores must have the same length")
    order = sorted(range(len(keys)), key=lambda index: -scores[index])
    return [keys[index] for index in order]
