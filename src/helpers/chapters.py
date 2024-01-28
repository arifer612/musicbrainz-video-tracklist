"""An abstract Chapers object."""

from abc import ABC, abstractmethod, abstractproperty
from ..main import default_file_extensions

import datetime as dt
import os


def subtract_time(time_init: str, time_final: str) -> str:
    init_time = dt.datetime.strptime(time_init, "%H:%M:%S.%f")
    final_time = dt.datetime.strptime(time_final, "%H:%M:%S.%f")
    time_diff = final_time - init_time
    return "{:02}:{:02}".format(
        time_diff.seconds % 3600//60,
        time_diff.seconds % 60,
    )


class Chapters(ABC):
    file: str

    @abstractproperty
    def chapters(self) -> list:
        return []

    @staticmethod
    @abstractmethod
    def get_chapter_string(chapter: list) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def get_chapter_time(chapter: list) -> tuple[str, str]:
        return "", ""

    def validate_file(self) -> None:
        """Validate if the chapter file is """
        file_ext = os.path.splitext(self.file)[1]
        if default_file_extensions.get(self.__class__.__name__) != file_ext:
            raise TypeError(
                f"{self.__class__.__name__} chapters need to be "
                f"{default_file_extensions.get(self.__class__.__name__)} files."
            )

    def print_chapters(self) -> str:
        """Print the chapter title and duration, given functions that read the
        titles and initial & final timestamps."""
        chapters = []
        for chapter_num, chapter_data in enumerate(self.chapters, 1):
            chapters.append(
                f"{chapter_num}. "
                f"{self.get_chapter_string(chapter_data)} "
                f"({subtract_time(*self.get_chapter_time(chapter_data))})"
            )
        if len(chapters) == 0:
            raise ValueError(f"{self.file} has no chapters!")
        return "\n".join(chapters)

    def __str__(self) -> str:
        return self.print_chapters()
