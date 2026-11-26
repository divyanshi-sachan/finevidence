from finevidence.data.numbers import canonicalize_numbers
from finevidence.generation.perturbations import thousands_separators


def test_separators_are_removed_only_in_well_formed_groups():
    text = "$ 1,234.5 and 12,345,678 but 3,1 and 2008,2009 and (1,000)"
    assert canonicalize_numbers(text) == "$ 1234.5 and 12345678 but 3,1 and 2008,2009 and (1000)"


def test_unicode_minus_and_spaces_become_ascii():
    assert canonicalize_numbers("− 5 %") == "- 5 %"


def test_finqa_style_text_is_unchanged_and_separators_round_trip():
    text = "row: revenue | 2009: $ 2457.5 | 2008: 1234567 | change: ( 12 ) %"
    assert canonicalize_numbers(text) == text
    assert canonicalize_numbers(thousands_separators(text)) == text
