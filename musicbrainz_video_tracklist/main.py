"""The main library of the project."""


import re
from functools import reduce
from typing import Any, Callable


def fraction_to_float(fraction: str) -> float:
    """Convert a string fraction to a floating number.

    Parameters
    ----------
    fraction: str
        A string representing a fraction.

    Returns
    -------
        The fraction as a float

    """
    components = [float(component) for component in fraction.split("/")]
    return reduce(lambda x, y: x / y, components)


def sanitise_title(title: str) -> str:
    """Read the chapter title and sanitise it.

    Leading chapter indices ending with "`.`", "`)`", "`]`", or enclosed within
    "`[]`" are removed. Titles starting with numbers that are not clearly
    chapter indices and single word chapter titles will be left untouched.

    Examples
    --------
    - ``'1. 02. [03...] 4) 5] 25 Days to Christmas' --> '25 Days to Christmas'``
    - ``24 Days to Christmas --> 24 Days to Christmas``
    - ``23 --> 23``

    Parameters
    ----------
    title: str
        The title to be sanitised.

    Raises
    ------
    ValueError
        When the title is empty.
    TypeError
        When the title is of the wrong type, e.g., list, dict, etc.

    Returns
    -------
        A sanitised title.

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
    """An object containing the chapters of a video file.

    Parameters
    ----------
    file_path:
        The path to the video file.
    prober:
        A callable function that takes in a `file` and returns a dict.

    """

    def __init__(self, file_path: str, prober: Callable[[str], Any]):
        self.file_path = file_path
        self.prober = prober

    @property
    def chapters(self) -> list[dict]:
        """The list of chapters as probed by the prober.

        Raises
        ------
        ffprobe3.exceptions.FFprobeMediaFileError
            When the file is missing or not a media file.

        See Also
        --------
        prober :
            Its output should contain a `chapters` key, of which its value is a
            list of dict.

        """
        metadata = self.prober(self.file_path)
        if "chapters" not in metadata:
            raise KeyError(f"{self.file_path} does not have chapters.")
        if not metadata["chapters"]:
            raise ValueError(f"{self.file_path} does not have chapters.")
        return metadata["chapters"]

    @staticmethod
    def get_chapter_string(chapter: dict) -> str:
        """Get the title of the chapter.

        Parameters
        ----------
        chapter :
            A dictionary object that contains information of a chapter,
            elements of the output of `Chapters.chapters`.

        See Also
        --------
        chapters :
            A chapter is an element of chapters.

        """
        try:
            title = chapter["tags"]["title"]
            if title:
                return sanitise_title(title)
            return f"Chapter {chapter['id']}"
        except KeyError:
            return f"Chapter {chapter['id']}"

    def get_chapter_timedelta(self, chapter: dict) -> str:
        """Get the length of each chapter.

        Parameters
        ----------
        chapter :
            A dictionary object that contains information of a chapter,
            elements of the output of `Chapters.chapters`.

        Returns
        -------
            The time duration of each chapter.

        See Also
        --------
        chapters :
            A chapter is an element of chapters.

        """
        if any(key not in chapter for key in ["time_base", "start", "end"]):
            raise KeyError(f"Start/End time is missing for {self.file_path}.")
        time_diff = chapter["end"] - chapter["start"]
        time_base = fraction_to_float(chapter["time_base"])
        time_diff_seconds = int(time_diff * time_base)
        return f"{time_diff_seconds % 3600//60:02}:{time_diff_seconds % 60:02}"

    def print_chapters(self) -> str:
        """Print the chapter title and duration, given functions that read the
        titles and initial & final timestamps.

        Returns
        -------
            The chapters in a format parsed as a tracklist for MusicBrainz.

        """
        chapters_to_print = [
            f"{chapter_num}. "
            f"{self.get_chapter_string(chapter_data)} "
            f"({self.get_chapter_timedelta(chapter_data)})"
            for chapter_num, chapter_data in enumerate(self.chapters, 1)
        ]
        return "\n".join(chapters_to_print)

    def __str__(self) -> str:
        return self.print_chapters()
