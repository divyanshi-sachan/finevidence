"""Executor-verified program selection for self-training (rejection-sampling fine-tuning).

Programs sampled from the current generator on *training* records are kept as extra training
targets only when they execute to the record's gold answer and every numeric literal appears in the
facts the model was shown, so a coincidentally correct constant is not rewarded. The gold
program and duplicates (after whitespace normalisation) are dropped, and at most ``cap``
programs are kept per record, in sampling order. Reads training labels only; never call it on
dev or test.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from finevidence.generation.inputs import GeneratorExample, build_keyed_example
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


def load_verified_programs(path: Path) -> dict[str, tuple[tuple[str, ...], tuple[str, ...]]]:
    """Notebook 20 output as ``{record_id: (fact_keys, verified_programs)}``; empty rows dropped."""
    verified: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        row = json.loads(line)
        if row["record_id"] in verified:
            raise ValueError(f"line {line_number}: duplicate record {row['record_id']!r}")
        if row["verified"]:
            verified[row["record_id"]] = (tuple(row["fact_keys"]), tuple(row["verified"]))
    return verified


def audit_verified_programs(
    records: Sequence[Mapping[str, Any]],
    verified: Mapping[str, tuple[Sequence[str], Sequence[str]]],
    *,
    cap: int,
    excluded_ids: Iterable[str] = (),
) -> dict[str, int]:
    """Re-check every verified program against ``records`` (train); raise on any violation.

    Each record id must be a train id and not in ``excluded_ids`` (dev and test ids); each
    program must still pass ``select_verified_programs`` on the facts it was sampled with.
    """
    by_id = {str(record["id"]): record for record in records}
    excluded = set(excluded_ids)
    programs = 0
    for record_id, (keys, kept) in verified.items():
        if record_id not in by_id or record_id in excluded:
            raise ValueError(f"{record_id!r} is not an exclusively-train record")
        example = build_keyed_example(by_id[record_id], keys, None)
        if list(kept) != select_verified_programs(
            by_id[record_id], kept, example.fact_texts, cap=cap
        ):
            raise ValueError(f"{record_id!r} has a program that no longer verifies")
        programs += len(kept)
    return {"records_with_new_program": len(verified), "new_programs": programs}


def self_training_examples(
    records: Sequence[Mapping[str, Any]],
    verified: Mapping[str, tuple[Sequence[str], Sequence[str]]],
    *,
    epoch: int,
) -> list[GeneratorExample]:
    """At most one extra example per record per epoch: verified program ``epoch mod n``.

    The input replays the facts the program was verified on, so its literals stay grounded.
    Rotating programs keeps a record with 4 verified programs at the same weight as one with 1.
    """
    examples = []
    for record in records:
        entry = verified.get(str(record["id"]))
        if entry:
            keys, kept = entry
            examples.append(build_keyed_example(record, keys, kept[epoch % len(kept)]))
    return examples
