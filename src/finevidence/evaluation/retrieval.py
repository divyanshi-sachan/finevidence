"""Within-record evidence retrieval metrics against ``gold_inds`` keys."""

from __future__ import annotations

from collections.abc import Collection, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalRecall:
    """Whether any and all gold keys appear among the top-k ranked keys."""

    k: int
    any_gold: bool
    all_gold: bool
    gold_count: int


def gold_recall_at_k(
    ranked_keys: Sequence[str], gold_keys: Collection[str], k: int
) -> RetrievalRecall:
    """Score one record's ranking; raw gold keys are compared verbatim, never repaired."""
    if k < 1:
        raise ValueError("k must be at least 1")
    if not gold_keys:
        raise ValueError("gold_keys must be non-empty; report such records separately")
    top = set(ranked_keys[:k])
    hits = [key in top for key in gold_keys]
    return RetrievalRecall(k, any(hits), all(hits), len(gold_keys))
