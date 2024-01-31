"""The main library of the project."""


import re
from functools import reduce
from typing import Any, Callable


def fraction_to_float(fraction: str) -> float:
    """Convert a string fraction to a floating number."""
    components = [float(component) for component in fraction.split("/")]
    return reduce(lambda x, y: x / y, components)


def sanitise_title(title: str) -> str:
    """Read the chapter title and sanitise it.

    For example,
    - '1. Chapter Title 1' --> 'Chapter Title 1'
    - '01. Chapter Title 1' --> 'Chapter Title 1'
    - '1. 2. Chapter Title 1' --> '2. Chapter Title 1'
    - '[1] Chapter Title 1' --> 'Chapter Title 1'
    - '[01] Chapter Title 1' --> 'Chapter Title 1'
    - '1) Chapter Title 1' --> 'Chapter Title 1'
    - '01) Chapter Title 1' --> 'Chapter Title 1'
    - 'Chapter Title 1' --> 'Chapter Title 1'
    - ':1: Chapter Title 1' --> ':1: Chapter Title 1'
    - '1 Day to Christmas' --> '1 Day to Christmas'
    - '2B Pencils are Good' --> '2B Pencils are Good'

    """
    if not title:
        raise ValueError("The title must not be empty.")
    try:
        first_chunk, second_chunk = title.split(None, 1)
        end_symbol_regex = r"[.)\]\}:]"
        regexes = [
            rf"\d+{end_symbol_regex}+",  # starts with digits, ends with .)]}:
            rf"\[\d+[.)\}}:]*\]{end_symbol_regex}*",  # within brackets
            r"\[\d+[.\]\}:]*\){end_symbol_regex}*",  # within parentheses
            r"\[\d+[.)\]:]*\}}{end_symbol_regex}*",  # within braces
        ]
        if re.search(rf'^({"|".join(regexes)})$', first_chunk):
            return sanitise_title(second_chunk)
        return title
    except ValueError:
        return title
    except AttributeError as exc:
        raise TypeError("The title must be a string.") from exc


class Chapters:
    """An object containing the chapters of a video file."""

    def __init__(self, file_path: str, prober: Callable[[str], Any]):
        self.file = file_path
        self.prober = prober

    @property
    def chapters(self) -> list:
        """Get the list of chapters using an appropriate prober.

        Raises:
        ffprobe3.exceptions.FFprobeMediaFileError when the file is missing or
        not a media file.
        """
        metadata = self.prober(self.file)
        if "chapters" not in metadata:
            raise KeyError(f"{self.file} does not have chapters.")
        if not metadata["chapters"]:
            raise ValueError(f"{self.file} does not have chapters.")
        return metadata["chapters"]

    @staticmethod
    def get_chapter_string(chapter: dict) -> str:
        """Get the title of the chapter."""
        try:
            title = chapter["tags"]["title"]
            if title:
                return sanitise_title(title)
            return f"Chapter {chapter['id']}"
        except KeyError:
            return f"Chapter {chapter['id']}"

    def get_chapter_timedelta(self, chapter: dict) -> str:
        """Get the length of each chapter."""
        if any(key not in chapter for key in ["time_base", "start", "end"]):
            raise KeyError(f"Start/End time is missing for {self.file}.")
        time_diff = chapter["end"] - chapter["start"]
        time_base = fraction_to_float(chapter["time_base"])
        time_diff_seconds = int(time_diff * time_base)
        return f"{time_diff_seconds % 3600//60:02}:{time_diff_seconds % 60:02}"

    def print_chapters(self) -> str:
        """Print the chapter title and duration, given functions that read the
        titles and initial & final timestamps."""
        chapters_to_print = [
            f"{chapter_num}. "
            f"{self.get_chapter_string(chapter_data)} "
            f"({self.get_chapter_timedelta(chapter_data)})"
            for chapter_num, chapter_data in enumerate(self.chapters, 1)
        ]
        return "\n".join(chapters_to_print)

    def __str__(self) -> str:
        return self.print_chapters()
