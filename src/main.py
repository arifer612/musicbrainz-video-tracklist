### main.py
## The main library of the project

from .helper import *
from typing import Callable, Any

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


def file_extension(file_path: str) -> str:
    """Get the file extension as a string."""
    return os.path.splitext(file_path)[1]


def _print_chapters(
        chapters: list,
        str_getter: Callable[[Any], str],
        time_getter: Callable[[Any], tuple[str, str]]
) -> None:
    """Print the chapter title and duration, given functions that read the
    titles and initial & final timestamps."""
    for chapter_num, chapter_data in enumerate(chapters, 1):
        print(
            f"{chapter_num}. "
            f"{str_getter(chapter_data)} "
            f"({subtract_time(*time_getter(chapter_data))})"
        )


def _read_file(file_path: str, read_getter: Callable[[str], list]) -> list:
    """Read the chapters with an appropriate file reader."""
    return read_getter(file_path)


def read_and_print(file_path: str) -> None:
    """Read the chapters."""
    file_ext = file_extension(file_path)
    if file_ext == ".xml":
        chapters = _read_file(file_path, mkv__read_file)
        _print_chapters(chapters, mkv__get_chapter_string, mkv__get_chapter_time)
    else:
        raise TypeError("Only MKV chapters are supported at the moment.")
