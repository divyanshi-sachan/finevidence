"""Small, explicit loaders for an inspected local FinQA release."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path


def load_finqa_split(path: Path) -> list[dict[str, object]]:
    """Load a FinQA split and validate its observed top-level structure.

    This intentionally does not assume detailed fields beyond a list of JSON
    object records. Field-level inspection remains part of the M2 audit.
    """
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON list in {path}, got {type(payload).__name__}.")

    invalid_indexes = [
        index for index, record in enumerate(payload) if not isinstance(record, Mapping)
    ]
    if invalid_indexes:
        preview = ", ".join(str(index) for index in invalid_indexes[:5])
        raise ValueError(
            f"Expected object records in {path}; non-object records at indexes: {preview}."
        )

    return [dict(record) for record in payload]
