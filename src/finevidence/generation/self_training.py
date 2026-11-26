"""Executor-verified program selection for self-training (rejection-sampling fine-tuning).

Programs sampled from the current generator on *training* records are kept as extra training
targets only when they execute to the record's gold answer and every numeric literal appears in the
facts the model was shown, so a coincidentally correct constant is not rewarded. The gold
program and duplicates (after whitespace normalisation) are dropped, and at most ``cap``
programs are kept per record, in sampling order. Reads training labels only; never call it on
dev or test.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from finevidence.generation.scoring import score_program_prediction


def _normalise(program: str) -> str:
    return " ".join(program.replace(" ,", ",").split())


def select_verified_programs(
    record: Mapping[str, Any],
    candidates: Iterable[str | None],
    fact_texts: Sequence[str],
    *,
    cap: int,
) -> list[str]:
    """Distinct, correct, fully grounded candidates other than the gold program, up to ``cap``."""
    if cap < 1:
        raise ValueError("cap must be at least 1")
    seen = {_normalise(record["qa"]["program"])}
    kept: list[str] = []
    for candidate in candidates:
        if candidate is None or _normalise(candidate) in seen:
            continue
        seen.add(_normalise(candidate))
        score = score_program_prediction(record, candidate, fact_texts)
        if score.execution_correct and score.grounded_literals == score.literals:
            kept.append(candidate)
            if len(kept) == cap:
                break
    return kept
