"""The main library of the project."""

from . import helpers
import os


default_file_extensions = {
    "MKV": ".xml",
    "MP4": ".txt",
}


def file_extension(file_path: str) -> str:
    """Get the file extension as a string."""
    return os.path.splitext(file_path)[1]


def print_chapters(file_path: str) -> None:
    """Print the chapters."""
    file_ext = file_extension(file_path)
    if file_ext == ".xml":
        chapters_file = helpers.MKV(file_path)
    elif file_ext == ".txt":
        chapters_file = helpers.MP4(file_path)
    else:
        raise TypeError("Only MKV and MP4 chapters are supported at the moment.")
    print(chapters_file)
