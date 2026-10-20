import json

import pytest

from finevidence import __version__
from finevidence.data import load_finqa_split, validate_records


def test_package_imports() -> None:
    assert __version__ == "0.1.0"


def test_validation_reports_non_mapping_records() -> None:
    assert validate_records([{"question": "What is revenue?"}, "invalid"]) == [
        "Record 1 is not a mapping."
    ]


def test_load_finqa_split_accepts_object_records(tmp_path) -> None:
    split_path = tmp_path / "train.json"
    split_path.write_text(json.dumps([{"id": "example-1", "qa": {}}]), encoding="utf-8")

    assert load_finqa_split(split_path) == [{"id": "example-1", "qa": {}}]


def test_load_finqa_split_rejects_non_object_records(tmp_path) -> None:
    split_path = tmp_path / "invalid.json"
    split_path.write_text(json.dumps(["not an object"]), encoding="utf-8")

    with pytest.raises(ValueError, match="non-object records"):
        load_finqa_split(split_path)
