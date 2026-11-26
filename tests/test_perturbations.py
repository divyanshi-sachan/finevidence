import pytest

from finevidence.generation.inputs import GeneratorExample, format_generator_source
from finevidence.generation.perturbations import (
    perturb_example,
    reword_question,
    thousands_separators,
)

QUESTION = "what was the percentage change in the total revenue?"
FACTS = ("revenue in 2009 was $ 1234.5", "revenue in 2008 was $ 1000")
EXAMPLE = GeneratorExample("r1", format_generator_source(QUESTION, FACTS), ("a", "b"), FACTS)


def test_reword_changes_surface_only_once_per_opening():
    assert reword_question(QUESTION) == "what is the percent change in the overall revenue"
    assert reword_question("what is the ratio") == "what was the ratio ?"


def test_thousands_separators_keep_values_and_years():
    text = "$ 2457.5 and 1234567 in 2009 , 999 and 0.12345"
    assert thousands_separators(text) == "$ 2,457.5 and 1,234,567 in 2009 , 999 and 0.12345"


def test_perturbations_rebuild_source_and_facts():
    reversed_ = perturb_example(EXAMPLE, QUESTION, "reverse_facts")
    assert reversed_.fact_texts == FACTS[::-1]
    assert reversed_.source == format_generator_source(QUESTION, FACTS[::-1])
    assert "1,234.5" in perturb_example(EXAMPLE, QUESTION, "thousands_separators").source
    foreign = perturb_example(EXAMPLE, QUESTION, "foreign_fact", "other record fact")
    assert foreign.fact_texts[0] == "other record fact" and foreign.record_id == "r1"


def test_unknown_or_incomplete_perturbation_is_rejected():
    with pytest.raises(ValueError):
        perturb_example(EXAMPLE, QUESTION, "rescale")
    with pytest.raises(ValueError):
        perturb_example(EXAMPLE, QUESTION, "foreign_fact")
