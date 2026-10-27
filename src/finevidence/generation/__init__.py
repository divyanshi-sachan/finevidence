"""Input construction and configuration for program-generation experiments."""

from .config import GeneratorConfig, load_generator_config, verify_rankings_file
from .inputs import (
    GeneratorExample,
    build_oracle_examples,
    build_retrieved_examples,
    build_training_examples,
    format_generator_source,
    load_rankings,
)
from .scoring import ProgramPredictionScore, score_program_prediction, summarize_scores

__all__ = [
    "GeneratorConfig",
    "GeneratorExample",
    "ProgramPredictionScore",
    "build_oracle_examples",
    "build_retrieved_examples",
    "build_training_examples",
    "format_generator_source",
    "load_generator_config",
    "load_rankings",
    "score_program_prediction",
    "summarize_scores",
    "verify_rankings_file",
]
