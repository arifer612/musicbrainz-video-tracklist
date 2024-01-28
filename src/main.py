"""The main library of the project."""

from typing import Callable, Any

import ffprobe3


def fraction_to_float(fraction: str) -> float:
    """Convert a string fraction to a floating number."""
    components = fraction.split('/')
    if len(components) != 2:
        raise ValueError("There is more than one decimal point in the fraction.")
    return float(int(components[0])/int(components[1]))


class Chapters():
    def __init__(self, file_path: str, prober: Callable[[str], Any]):
        self.file = file_path
        self.prober = prober

    @property
    def chapters(self) -> list:
        """Get the list of chapters using an appropriate prober."""
        metadata = self.prober(self.file)
        if "chapters" not in metadata or not len(metadata['chapters']):
            raise KeyError(f"{self.file} does not have chapters.")
        return metadata['chapters']

    @staticmethod
    def get_chapter_string(chapter: dict) -> str:
        """Get the title of the chapter."""
        try:
            return chapter['tags']['title']
        except KeyError:
            return f"Chapter {chapter['id']}"

    def get_chapter_timedelta(self, chapter: dict) -> str:
        """Get the length of each chapter."""
        if any(key not in chapter for key in ['time_base', 'start', 'end']):
            raise KeyError(f"Start/End time is missing for {self.file}.")
        time_diff = (chapter['end'] - chapter['start'])
        time_base = fraction_to_float(chapter['time_base'])
        time_diff_seconds = int(time_diff * time_base)
        return "{:02}:{:02}".format(
            time_diff_seconds % 3600//60,
            time_diff_seconds % 60,
        )

    def print_chapters(self) -> str:
        """Print the chapter title and duration, given functions that read the
        titles and initial & final timestamps."""
        chapters_to_print = [
            f"{chapter_num}. "
            f"{self.get_chapter_string(chapter_data)} "
            f"({self.get_chapter_timedelta(chapter_data)})"
            for chapter_num, chapter_data in enumerate(self.chapters, 1)
        ]
        if len(chapters_to_print) == 0:
            raise ValueError(f"{self.file} has no chapters!")
        return "\n".join(chapters_to_print)

    def __str__(self) -> str:
        return self.print_chapters()


def print_chapters(file_path: str) -> None:
    """Print the chapters."""
    chapters = Chapters(file_path, ffprobe3.probe)
    try:
        print(chapters)
    except ValueError as ve:
        print(ve)
    except KeyError as ke:
        print(ke)
