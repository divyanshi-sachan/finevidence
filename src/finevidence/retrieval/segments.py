"""Evidence segments built from the allowlisted raw context of one FinQA record."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from finevidence.data.preprocessing import build_structured_input
from finevidence.reasoning.arithmetic import NumericCandidate, parse_numeric_candidate

TEXT_NUMBER_SPAN = re.compile(r"(?<![\w.])[-+]?(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+)%?(?![\w.])")


@dataclass(frozen=True)
class EvidenceSegment:
    """One retrievable table row or sentence, keyed like FinQA ``gold_inds``.

    ``table_n`` is raw table row ``n``; ``text_n`` indexes ``pre_text + post_text``.
    """

    key: str
    source: str
    text: str
    cells: tuple[str, ...] = ()
    header: tuple[str, ...] = ()


def build_evidence_segments(
    record: Mapping[str, Any], *, include_header_row: bool = False
) -> list[EvidenceSegment]:
    """Build table-row and sentence segments without reading any annotation field.

    The header row (``table_0``) is excluded by default, matching Notebooks 06-08.
    Some gold evidence references it, so retrieval training can opt in.
    """
    source = build_structured_input(record)
    table = source["table"]
    header = tuple(str(cell) for cell in table[0]) if table else ()
    first_row = 0 if include_header_row else 1
    segments = [
        EvidenceSegment(
            key=f"table_{index}",
            source="table",
            text=" | ".join(str(cell) for cell in row),
            cells=tuple(str(cell) for cell in row),
            header=header,
        )
        for index, row in enumerate(table[first_row:], start=first_row)
    ]
    segments.extend(
        EvidenceSegment(key=f"text_{index}", source="text", text=str(sentence))
        for index, sentence in enumerate(source["pre_text"] + source["post_text"])
    )
    return segments


def segment_numeric_candidates(segment: EvidenceSegment) -> list[NumericCandidate]:
    """Parse value cells of a table row (skipping its label) or numeric spans of a sentence."""
    if segment.source == "table":
        raw_values = segment.cells[1:]
    else:
        raw_values = tuple(match.group() for match in TEXT_NUMBER_SPAN.finditer(segment.text))
    return [
        parse_numeric_candidate(raw, source_id=segment.key, context=segment.text)
        for raw in raw_values
    ]
