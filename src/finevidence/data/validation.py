"""Small, schema-agnostic validation helpers for early dataset inspection."""

from collections.abc import Iterable, Mapping


def validate_records(records: Iterable[Mapping[str, object]]) -> list[str]:
    """Report basic structural issues without assuming an unverified FinQA schema.

    The official dataset's fields will be represented explicitly only after its
    downloaded version is inspected. This guard helps notebooks fail early when a
    local JSON loader yields non-mapping records.
    """
    issues: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            issues.append(f"Record {index} is not a mapping.")
    return issues
