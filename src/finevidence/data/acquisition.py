"""Download the pinned public FinQA splits and verify them against recorded checksums.

This mirrors the Notebook 02 acquisition rules for non-notebook runtimes (e.g. Colab or
Kaggle): commit-pinned URLs, JSON validation before the final move, no overwriting, and
SHA-256 verification against ``docs/dataset-card.md``. ``private_test.json`` is never fetched.
Run with ``python -m finevidence.data.acquisition [--include-test]``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import BinaryIO
from urllib.request import urlopen

FINQA_REVISION = "0f16e2867befa6840783e58be38c9efb9229d742"
PINNED_SHA256 = {
    "train": "49f237eb9779b569473b26b08048867d04635a7cc39ad6a7a5664c55bb428db6",
    "dev": "a847fb7e0d61a3125a1e2909852df6b89f1ee64d2c5ff1bf689e332214deee51",
    "test": "831dbfb2e785dbc227f895ce3f24046433467aec67b09db2bd6ac7692a8a30dc",
}
# Model development needs train and dev only; test is fetched only when asked for.
DEVELOPMENT_SPLITS = ("train", "dev")


def split_url(split: str) -> str:
    return f"https://raw.githubusercontent.com/czyssrs/FinQA/{FINQA_REVISION}/dataset/{split}.json"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify(path: Path, split: str) -> None:
    actual = file_sha256(path)
    if actual != PINNED_SHA256[split]:
        raise ValueError(f"{path} has SHA-256 {actual}, expected {PINNED_SHA256[split]}")
    with path.open(encoding="utf-8") as file:
        if not isinstance(json.load(file), list):
            raise ValueError(f"expected a JSON list in {path}")


def download_finqa_splits(
    raw_dir: Path,
    splits: Iterable[str] = DEVELOPMENT_SPLITS,
    *,
    opener: Callable[[str], BinaryIO] = urlopen,
) -> dict[str, str]:
    """Fetch missing pinned splits into ``raw_dir`` and verify every requested split."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    states: dict[str, str] = {}
    for split in splits:
        if split not in PINNED_SHA256:
            raise ValueError(f"unknown public split: {split!r}")
        destination = raw_dir / f"{split}.json"
        if destination.exists():
            _verify(destination, split)
            states[split] = "existing; verified, not overwritten"
            continue
        with tempfile.NamedTemporaryFile(dir=raw_dir, prefix=f".{split}.", delete=False) as handle:
            temporary = Path(handle.name)
        try:
            with opener(split_url(split)) as response, temporary.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
            _verify(temporary, split)
            if destination.exists():
                raise FileExistsError(f"refusing to overwrite {destination}")
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
        states[split] = "downloaded; verified"
    return states


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--include-test", action="store_true", help="also fetch the test split")
    arguments = parser.parse_args()
    splits = (*DEVELOPMENT_SPLITS, "test") if arguments.include_test else DEVELOPMENT_SPLITS
    for split, state in download_finqa_splits(arguments.raw_dir, splits).items():
        print(f"{split}: {state}")


if __name__ == "__main__":
    main()
