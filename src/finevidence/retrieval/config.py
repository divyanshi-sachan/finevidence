"""Typed, validated loading of retriever experiment configuration."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

MODEL_DIR_ENVIRONMENT_VARIABLE = "FINEVIDENCE_MODEL_DIR"
_NEGATIVE_SAMPLING = frozenset({"random", "tfidf_hard"})


@dataclass(frozen=True)
class RetrieverConfig:
    experiment_name: str
    seed: int
    dataset_root: Path
    train_split: str
    evaluation_split: str
    pretrained_name: str
    max_seq_length: int
    negatives_per_positive: int
    negative_sampling: str
    epochs: int
    batch_size: int
    learning_rate: float
    warmup_ratio: float
    include_header_row: bool
    recall_k: tuple[int, ...]
    top_n_for_generator: int
    model_dir: Path
    predictions_path: Path


def load_retriever_config(
    path: Path, *, environment: Mapping[str, str] = os.environ
) -> RetrieverConfig:
    """Load a retriever TOML file; ``FINEVIDENCE_MODEL_DIR`` overrides ``output.model_dir``."""
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    model, training = raw["model"], raw["training"]
    evaluation, output = raw["evaluation"], raw["output"]
    config = RetrieverConfig(
        experiment_name=raw["experiment_name"],
        seed=raw["seed"],
        dataset_root=Path(raw["dataset_root"]),
        train_split=raw["train_split"],
        evaluation_split=raw["evaluation_split"],
        pretrained_name=model["pretrained_name"],
        max_seq_length=model["max_seq_length"],
        negatives_per_positive=training["negatives_per_positive"],
        negative_sampling=training["negative_sampling"],
        epochs=training["epochs"],
        batch_size=training["batch_size"],
        learning_rate=float(training["learning_rate"]),
        warmup_ratio=float(training["warmup_ratio"]),
        include_header_row=training["include_header_row"],
        recall_k=tuple(evaluation["recall_k"]),
        top_n_for_generator=evaluation["top_n_for_generator"],
        model_dir=Path(environment.get(MODEL_DIR_ENVIRONMENT_VARIABLE) or output["model_dir"]),
        predictions_path=Path(output["predictions_path"]),
    )
    _validate(config)
    return config


def _validate(config: RetrieverConfig) -> None:
    if config.evaluation_split == "test" or config.train_split == "test":
        raise ValueError("retriever development must not use the official test split")
    if config.train_split == config.evaluation_split:
        raise ValueError("train and evaluation splits must differ")
    if config.negative_sampling not in _NEGATIVE_SAMPLING:
        raise ValueError(f"negative_sampling must be one of {sorted(_NEGATIVE_SAMPLING)}")
    positive_integers = {
        "max_seq_length": config.max_seq_length,
        "negatives_per_positive": config.negatives_per_positive,
        "epochs": config.epochs,
        "batch_size": config.batch_size,
        "top_n_for_generator": config.top_n_for_generator,
    }
    for name, value in positive_integers.items():
        if not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    if not config.recall_k or any(k < 1 for k in config.recall_k):
        raise ValueError("recall_k must contain positive integers")
    if not 0 < config.learning_rate < 1 or not 0 <= config.warmup_ratio < 1:
        raise ValueError("learning_rate must be in (0, 1) and warmup_ratio in [0, 1)")
