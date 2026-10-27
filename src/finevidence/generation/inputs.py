"""Source/target construction for a FinQA program generator.

Three input conditions share one source format, ``question: ... facts: [1] ... [2] ...``:

- **training**: gold segments plus seeded random distractors from the same record,
  shuffled so a fact's position carries no label information; the target is ``program``.
- **retrieved**: the top-ranked segments from a retriever ranking file (prediction time;
  no annotation field is read).
- **gold-facts oracle**: only the gold segments. Not a prediction system: it reads
  ``gold_inds`` keys to bound generator quality independently of retrieval.

Facts are always rendered from the raw context by key (``segment_retrieval_text``), never
from the annotated ``gold_inds`` text.
"""

from __future__ import annotations

import json
import random
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from finevidence.data.preprocessing import build_structured_input
from finevidence.retrieval.pairs import build_ranking_pairs


@dataclass(frozen=True)
class GeneratorExample:
    """One generator input; ``target`` is the gold program for training examples only."""

    record_id: str
    source: str
    fact_keys: tuple[str, ...]
    fact_texts: tuple[str, ...]
    target: str | None = None


def format_generator_source(question: str, fact_texts: Sequence[str]) -> str:
    facts = " ".join(f"[{index}] {text}" for index, text in enumerate(fact_texts, start=1))
    return f"question: {question} facts: {facts}"


def _segment_texts(record: Mapping[str, Any]) -> dict[str, str]:
    return {pair.key: pair.text for pair in build_ranking_pairs(record, include_header_row=True)}


def _example(
    record: Mapping[str, Any], keys: Sequence[str], texts: Mapping[str, str], target: str | None
) -> GeneratorExample:
    question = build_structured_input(record)["question"]
    fact_texts = tuple(texts[key] for key in keys)
    return GeneratorExample(
        record_id=str(record["id"]),
        source=format_generator_source(question, fact_texts),
        fact_keys=tuple(keys),
        fact_texts=fact_texts,
        target=target,
    )


def _gold_keys(record: Mapping[str, Any], texts: Mapping[str, str]) -> list[str]:
    """Gold keys present in the raw context, in segment order; invalid keys are dropped."""
    gold = set(record["qa"]["gold_inds"])
    return [key for key in texts if key in gold]


def build_training_examples(
    records: Iterable[Mapping[str, Any]], *, facts_per_input: int, seed: int
) -> list[GeneratorExample]:
    """Gold facts plus random same-record distractors up to ``facts_per_input``, shuffled.

    Records with more gold facts than ``facts_per_input`` keep all gold facts.
    """
    rng = random.Random(seed)
    examples = []
    for record in records:
        texts = _segment_texts(record)
        gold = _gold_keys(record, texts)
        others = [key for key in texts if key not in gold]
        distractors = rng.sample(others, min(len(others), max(0, facts_per_input - len(gold))))
        keys = [*gold, *distractors]
        rng.shuffle(keys)
        examples.append(_example(record, keys, texts, record["qa"]["program"]))
    return examples


def build_retrieved_examples(
    records: Iterable[Mapping[str, Any]],
    rankings: Mapping[str, Sequence[str]],
    *,
    facts_per_input: int,
) -> list[GeneratorExample]:
    """Top-ranked facts in ranking order; reads no annotation field."""
    examples = []
    for record in records:
        texts = _segment_texts(record)
        ranked = rankings[str(record["id"])]
        unknown = [key for key in ranked if key not in texts]
        if unknown:
            raise ValueError(f"ranking for {record['id']} has unknown keys: {unknown[:3]}")
        examples.append(_example(record, ranked[:facts_per_input], texts, None))
    return examples


def build_oracle_examples(records: Iterable[Mapping[str, Any]]) -> list[GeneratorExample]:
    """Gold facts only, in segment order. An upper-bound diagnostic, not a prediction system."""
    examples = []
    for record in records:
        texts = _segment_texts(record)
        examples.append(_example(record, _gold_keys(record, texts), texts, None))
    return examples


def load_rankings(path: Path) -> dict[str, list[str]]:
    """Load a Notebook 10 ranking file as ``{record_id: ranked_keys}``."""
    rankings: dict[str, list[str]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        row = json.loads(line)
        if not isinstance(row.get("id"), str) or not isinstance(row.get("ranked_keys"), list):
            raise ValueError(f"line {line_number}: expected 'id' and 'ranked_keys'")
        if row["id"] in rankings:
            raise ValueError(f"line {line_number}: duplicate id {row['id']!r}")
        rankings[row["id"]] = [str(key) for key in row["ranked_keys"]]
    return rankings
