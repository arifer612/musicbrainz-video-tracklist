"""Test the sanitise_title function in the main.py module"""

import pytest

from musicbrainz_video_tracklist.main import sanitise_title


def test_sanitise_multiple_indices():
    """A chapter title with multiple indices, e.g. [1] 2. 3) Chapter title
    should only be read as `Chapter title`."""
    assert (
        sanitise_title("[1..] 2))) 3. 25 Days to Christmas")
        == "25 Days to Christmas"
    )


def test_no_sanitise_if_contains_characters():
    """The sanitisation process should stop at the first sign of a non-digit or
    non-special character."""
    assert (
        sanitise_title("1. [2a] 3. 24 Days to Christmas")
        == "[2a] 3. 24 Days to Christmas"
    )


def test_already_sanitised_title():
    """No sanitisation is needed if there are no chapter indices."""
    assert sanitise_title("23 Days to Christmas") == "23 Days to Christmas"


def test_single_word_title():
    """No sanitisation if the title is only one word."""
    assert sanitise_title("Christmas") == "Christmas"


def test_single_digit_title():
    """No sanitisation if the title is a single number."""
    assert sanitise_title("00000") == "00000"


def test_single_index_title():
    """No sanitisation if the title is a single index."""
    assert sanitise_title("1.") == "1."


def test_no_title():
    with pytest.raises(ValueError):
        sanitise_title("")


def test_incorrect_title_type():
    with pytest.raises(TypeError):
        sanitise_title(["hi", "there"])  # type: ignore
