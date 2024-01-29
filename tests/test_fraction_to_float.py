"""Test the fraction_to_float function in the main.py module"""

import pytest

from musicbrainz_video_tracklist.main import fraction_to_float


def test_single_fraction():
    "A single fraction like 1/2 is valid."
    assert fraction_to_float("1/2") == 0.5


def test_multiple_fractions():
    "Multiple fractions like 1/2/5 are valid."
    assert fraction_to_float("1/2/5") == 0.1


def test_single_non_integral_fraction():
    "A non-integral fraction like 1/0.5 is valid."
    assert fraction_to_float("1/0.5") == 2.0


def test_multiple_non_integral_fractions():
    "Multiple non-integral fractions like 1/0.5/0.2 are valid."
    assert fraction_to_float("1/0.5/0.2") == 10.0


def test_string_in_fraction():
    "Fractions with strings are invalid."
    with pytest.raises(ValueError):
        fraction_to_float("1/four")


def test_incorrect_delimiter():
    "Fractions need to use `/`"
    with pytest.raises(ValueError):
        fraction_to_float("1|2")


def test_trivial_integral_fraction():
    "Trivial integral fractions, i.e., integers, are valid fractions."
    assert fraction_to_float("2") == 2


def test_trivial_non_integral_fractions():
    "Trivial non-integral fractions, i.e., floats, are valid fractions."
    assert fraction_to_float("0.5") == 0.5
