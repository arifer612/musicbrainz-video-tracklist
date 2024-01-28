"""Library of tools for manipulating mp4 files.

Chapter files are expected to be of the following format:
================================================
Source Duration               : Duration in ms
00:00:00.000                  : Chapter 1 title
00:00:10.000                  : Chapter 2 title
...
02:30:00.000                  : Chapter N title
================================================
This format can be obtained from mediainfo.
"""


import datetime

from .chapters import Chapters


class MP4(Chapters):
    def __init__(self, file_path: str):
        self.file = file_path
        self.validate_file()

    @property
    def chapters(self) -> list[tuple[str, str, str]]:
        """Parse a block of text containing chapter markers.

        Returns a list of tuples that contains the initial timestamp, final
        timestamp, and title of the chapter.
        """
        with open(self.file, 'r') as txt_file:
            text_block = txt_file.read()

        text_data = [
            text_column.strip()
            for text_line in text_block.splitlines()
            for text_column in text_line.split(" :")
        ]
        text_data.pop(0)
        text_data.append(self.get_total_duration(text_data.pop(0)))
        text_data.append("END")

        if len(text_data) % 2:
            raise IndexError(
                "The chapter markers are probably missing some chapter titles."
            )
        return [
            (
                text_data[2 * line_no],
                text_data[2 * line_no + 2],
                text_data[2 * line_no + 1]
            )
            for line_no in range(int(len(text_data) / 2) - 1)
        ]

    @staticmethod
    def get_total_duration(duration: str) -> str:
        """Read the total duration as milliseconds."""
        return str(datetime.timedelta(milliseconds=int(duration)))

    @staticmethod
    def get_chapter_time(chapter: tuple[str, str, str]) -> tuple[str, str]:
        """Read the chapter and get the initial and final timestamps."""
        return chapter[0], chapter[1]

    @staticmethod
    def get_chapter_string(chapter: tuple) -> str:
        """Read the chapter and get its title."""
        return chapter[2]
