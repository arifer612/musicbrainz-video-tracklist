"""Test the Chapters object in the main module."""

import json

import ffprobe3
import pytest

from musicbrainz_video_tracklist.main import Chapters

mock_ffprobe_response = '{"streams": ["some-streams"], "chapters": [{"id": 0, "time_base": "1/10000", "start": 0, "start_time": "0.000000", "end": 3629042, "end_time": "362.904200", "tags": {"title": "01. Chapter 1"}}, {"id": 1, "time_base": "1/10000", "start": 3629042, "start_time": "362.904200", "end": 4616695, "end_time": "461.669500", "tags": {"title": "2. Chapter 2"}}, {"id": 2, "time_base": "1/10000", "start": 4616695, "start_time": "461.669500", "end": 6832242, "end_time": "683.224200", "tags": {"title": "[03] Chapter 3"}}, {"id": 3, "time_base": "1/10000", "start": 6832242, "start_time": "683.224200", "end": 10070060, "end_time": "1007.006000", "tags": {"title": "[4] Chapter 4"}}, {"id": 4, "time_base": "1/10000", "start": 10070060, "start_time": "1007.006000", "end": 13283270, "end_time": "1328.327000", "tags": {"title": "05) Chapter 5"}}, {"id": 5, "time_base": "1/10000", "start": 13283270, "start_time": "1328.327000", "end": 16778845, "end_time": "1677.884500", "tags": {"title": "6) Chapter 6"}}, {"id": 6, "time_base": "1/10000", "start": 16778845, "start_time": "1677.884500", "end": 19629610, "end_time": "1962.961000", "tags": {"title": "Chapter 7"}}, {"id": 7, "time_base": "1/10000", "start": 19629610, "start_time": "1962.961000", "end": 22862840, "end_time": "2286.284000", "tags": {"title": ":8: Chapter 8"}}], "format": {"filename": "the-file-name"}}'

testChapters = Chapters("video_file", lambda _: json.loads(mock_ffprobe_response))


@pytest.fixture
def dummyChapters(request):
    """Replace keys in the valid mock_ffprobe_response with a `dummy' key."""
    return Chapters(
        "video_file",
        lambda _: json.loads(mock_ffprobe_response.replace(request.param, "dummy")),
    )


def test_probed_response_with_chapters():
    "When the probed response has chapters, the Chapters object is valid."
    assert testChapters.chapters


def test_probed_response_without_chapters_key():
    """When the probed response has no `chapters' key, the Chapters object
    should raise a KeyError.

    """
    noChaptersKey = Chapters(
        "video_file",
        lambda _: json.loads(mock_ffprobe_response.replace("chapters", "dummy")),
    )
    with pytest.raises(KeyError):
        noChaptersKey.chapters


def test_probed_response_with_no_chapters():
    """When the probed response has no chapters, the Chapters object should
    raise a ValueError.

    """
    missing_chapters = json.loads(mock_ffprobe_response)
    missing_chapters.update({"chapters": []})
    noChapters = Chapters("video_file", lambda _: missing_chapters)
    with pytest.raises(ValueError):
        noChapters.chapters


def test_get_chapter_string():
    "Get the chapter strings of the chapters in mock_ffprobe_response."
    chapter_titles = [
        testChapters.get_chapter_string(chapter) for chapter in testChapters.chapters
    ]
    assert chapter_titles == [
        "01. Chapter 1",
        "2. Chapter 2",
        "[03] Chapter 3",
        "[4] Chapter 4",
        "05) Chapter 5",
        "6) Chapter 6",
        "Chapter 7",
        ":8: Chapter 8",
    ]


def test_get_chapter_timedelta():
    "Get the chapter durations of the chapters in mock_ffprobe_response."
    chapter_durations = [
        testChapters.get_chapter_timedelta(chapter) for chapter in testChapters.chapters
    ]
    assert chapter_durations == [
        "06:02",
        "01:38",
        "03:41",
        "05:23",
        "05:21",
        "05:49",
        "04:45",
        "05:23",
    ]


def test_print_chapter():
    """Printing the Chapter object should print the chapters of the object, their
    time duration, and be indexed by integers."""
    assert str(testChapters) == "\n".join(
        [
            "1. 01. Chapter 1 (06:02)",
            "2. 2. Chapter 2 (01:38)",
            "3. [03] Chapter 3 (03:41)",
            "4. [4] Chapter 4 (05:23)",
            "5. 05) Chapter 5 (05:21)",
            "6. 6) Chapter 6 (05:49)",
            "7. Chapter 7 (04:45)",
            "8. :8: Chapter 8 (05:23)",
        ]
    )


@pytest.mark.parametrize("dummyChapters", ["time_base", "start", "end"], indirect=True)
def test_missing_timekeys(dummyChapters):
    """When the probed response chapters do not contain the keys `time_base`,
    `start`, or `end`, the response is invalid.

    """
    with pytest.raises(KeyError):
        [
            dummyChapters.get_chapter_timedelta(chapter)
            for chapter in dummyChapters.chapters
        ]


def test_printed_chapters_have_newlines():
    "The chapters of mock_ffprobe_response should have newlines."
    assert "\n" in testChapters.print_chapters()


def test_ffprobe_missing_file():
    """When the file is missing, the Chapters object should raise a
    ffprobe3.exceptions.FFprobeMediaFileError.

    """
    missingFile = Chapters("no_file_here", ffprobe3.probe)
    with pytest.raises(ffprobe3.exceptions.FFprobeMediaFileError):
        missingFile.chapters


def test_ffprobe_non_media_file():
    """When the file is not a media file, the Chapters object should raise a
    ffprobe3.exceptions.FFprobeMediaFileError.

    """
    nonMediaFile = Chapters("test/test_chapters.py", ffprobe3.probe)
    with pytest.raises(ffprobe3.exceptions.FFprobeMediaFileError):
        nonMediaFile.chapters


def test_get_chapter_string_with_no_title():
    """When the titles of the chapters are empty, the chapter strings should
    just be the chapter ID."""
    mock_ffprobe_response_no_titles = json.loads(mock_ffprobe_response)
    _ = [
        chapter.update({"tags": {"title": ""}})
        for chapter in mock_ffprobe_response_no_titles["chapters"]
    ]
    noTitles = Chapters("no_titles", lambda _: mock_ffprobe_response_no_titles)
    chapter_strings = [
        noTitles.get_chapter_string(chapter) for chapter in noTitles.chapters
    ]
    assert chapter_strings == [
        "Chapter 0",
        "Chapter 1",
        "Chapter 2",
        "Chapter 3",
        "Chapter 4",
        "Chapter 5",
        "Chapter 6",
        "Chapter 7",
    ]


@pytest.mark.parametrize("dummyChapters", ["tag", "title"], indirect=True)
def test_get_chapter_string_with_no_title_tag(dummyChapters):
    """When the chapters do not have a `title' key in the tags, or a `tags' key
    , the chapter string should be the chapter ID.

    """
    chapter_strings = [
        dummyChapters.get_chapter_string(chapter) for chapter in dummyChapters.chapters
    ]
    assert chapter_strings == [
        "Chapter 0",
        "Chapter 1",
        "Chapter 2",
        "Chapter 3",
        "Chapter 4",
        "Chapter 5",
        "Chapter 6",
        "Chapter 7",
    ]
