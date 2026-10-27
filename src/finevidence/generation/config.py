"""Typed, validated loading of program-generator experiment configuration."""

from __future__ import annotations

import os
import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from finevidence.data.acquisition import file_sha256

MODEL_DIR_ENVIRONMENT_VARIABLE = "FINEVIDENCE_MODEL_DIR"
RANKINGS_PATH_ENVIRONMENT_VARIABLE = "FINEVIDENCE_RANKINGS_PATH"
_SHA256 = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class GeneratorConfig:
    experiment_name: str
    seed: int
    dataset_root: Path
    train_split: str
    evaluation_split: str
    pretrained_name: str
    max_source_length: int
    max_target_length: int
    facts_per_input: int
    epochs: int
    batch_size: int
    micro_batch_size: int
    learning_rate: float
    warmup_ratio: float
    mixed_precision: bool
    num_beams: int
    eval_batch_size: int
    rankings_path: Path
    rankings_sha256: str
    model_dir: Path
    predictions_dir: Path


def load_generator_config(
    path: Path, *, environment: Mapping[str, str] = os.environ
) -> GeneratorConfig:
    """Load a generator TOML file; environment variables override the model and rankings paths."""
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    model, training, generation = raw["model"], raw["training"], raw["generation"]
    inputs, output = raw["inputs"], raw["output"]
    config = GeneratorConfig(
        experiment_name=raw["experiment_name"],
        seed=raw["seed"],
        dataset_root=Path(raw["dataset_root"]),
        train_split=raw["train_split"],
        evaluation_split=raw["evaluation_split"],
        pretrained_name=model["pretrained_name"],
        max_source_length=model["max_source_length"],
        max_target_length=model["max_target_length"],
        facts_per_input=training["facts_per_input"],
        epochs=training["epochs"],
        batch_size=training["batch_size"],
        micro_batch_size=training["micro_batch_size"],
        learning_rate=float(training["learning_rate"]),
        warmup_ratio=float(training["warmup_ratio"]),
        mixed_precision=training["mixed_precision"],
        num_beams=generation["num_beams"],
        eval_batch_size=generation["eval_batch_size"],
        rankings_path=Path(
            environment.get(RANKINGS_PATH_ENVIRONMENT_VARIABLE) or inputs["rankings_path"]
        ),
        rankings_sha256=inputs["rankings_sha256"],
        model_dir=Path(environment.get(MODEL_DIR_ENVIRONMENT_VARIABLE) or output["model_dir"]),
        predictions_dir=Path(output["predictions_dir"]),
    )
    _validate(config)
    return config


def verify_rankings_file(path: Path, expected_sha256: str) -> None:
    """Refuse a rankings file that is not the recorded Notebook 10 output."""
    actual = file_sha256(path)
    if actual != expected_sha256:
        raise ValueError(f"{path} has SHA-256 {actual}, expected {expected_sha256}")


def _validate(config: GeneratorConfig) -> None:
    if "test" in (config.train_split, config.evaluation_split):
        raise ValueError("generator development must not use the official test split")
    if config.train_split == config.evaluation_split:
        raise ValueError("train and evaluation splits must differ")
    positive_integers = {
        "max_source_length": config.max_source_length,
        "max_target_length": config.max_target_length,
        "facts_per_input": config.facts_per_input,
        "epochs": config.epochs,
        "batch_size": config.batch_size,
        "micro_batch_size": config.micro_batch_size,
        "eval_batch_size": config.eval_batch_size,
        "num_beams": config.num_beams,
    }
    for name, value in positive_integers.items():
        if not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    if config.batch_size % config.micro_batch_size:
        raise ValueError("batch_size must be a multiple of micro_batch_size")
    if not 0 < config.learning_rate < 1 or not 0 <= config.warmup_ratio < 1:
        raise ValueError("learning_rate must be in (0, 1) and warmup_ratio in [0, 1)")
    if not isinstance(config.mixed_precision, bool):
        raise ValueError("mixed_precision must be true or false")
    if not _SHA256.fullmatch(config.rankings_sha256):
        raise ValueError("rankings_sha256 must be a lowercase 64-character hex digest")
