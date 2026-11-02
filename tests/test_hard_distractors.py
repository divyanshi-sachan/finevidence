import random
from pathlib import Path

import pytest

from finevidence.generation import build_training_examples, load_generator_config


def _record() -> dict:
    return {
        "id": "H",
        "pre_text": ["interest expense rose in 2009 .", "the weather was mild ."],
        "post_text": ["revenue grew strongly .", "staff numbers were stable ."],
        "table": [["", "2009"], ["interest expense", "$ 40"], ["office count", "12"]],
        "qa": {
            "question": "what was the interest expense in 2009?",
            "gold_inds": {"table_1": "annotated"},
            "program": "add(40, 0)",
        },
    }


def test_full_hard_share_picks_facts_sharing_question_words():
    examples = build_training_examples(
        [_record()], facts_per_input=2, seed=1, hard_distractor_share=1
    )
    example = examples[0]
    assert set(example.fact_keys) == {"table_1", "text_0"}


def test_zero_share_keeps_the_original_random_sampling():
    record = _record()
    example = build_training_examples([record], facts_per_input=3, seed=5)[0]
    keys = ["table_0", "table_1", "table_2", "text_0", "text_1", "text_2", "text_3"]
    rng = random.Random(5)
    others = [key for key in keys if key != "table_1"]
    expected = ["table_1", *rng.sample(others, 2)]
    rng.shuffle(expected)
    assert list(example.fact_keys) == expected


def test_config_rejects_share_outside_unit_interval(tmp_path):
    base = Path(__file__).parents[1] / "configs" / "generator_t5_base.toml"
    text = base.read_text().replace(
        "facts_per_input = 5", "facts_per_input = 5\nhard_distractor_share = 1.5"
    )
    path = tmp_path / "bad.toml"
    path.write_text(text)
    with pytest.raises(ValueError, match="hard_distractor_share"):
        load_generator_config(path, environment={})
