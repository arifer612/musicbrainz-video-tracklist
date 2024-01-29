"""The main library of the project."""

from functools import reduce
from typing import Any, Callable


def fraction_to_float(fraction: str) -> float:
    """Convert a string fraction to a floating number."""
    components = [float(component) for component in fraction.split("/")]
    return reduce(lambda x, y: x / y, components)


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
                return title
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
