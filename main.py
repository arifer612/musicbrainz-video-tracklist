#!/usr/bin/env python
### mkv-chaps-to-mb.py
## Parse an MKV chapter XML file into a tracklist for MusicBrainz

import datetime as dt
import sys
import bs4


def subtract_time(time_init: str, time_final: str) -> str:
    init_time = dt.datetime.strptime(time_init[:-3], "%H:%M:%S.%f")
    final_time = dt.datetime.strptime(time_final[:-3], "%H:%M:%S.%f")
    time_diff = final_time - init_time
    return "{:02}:{:02}".format(
        time_diff.seconds % 3600//60,
        time_diff.seconds % 60,
    )


def get_chapter_time(chapter: bs4.element.Tag) -> str:
    """Read the chapter and get the timedelta."""
    try:
        init_time = chapter.find('ChapterTimeStart').text  # type: ignore [reportOptionalMemberAccess]
        final_time = chapter.find('ChapterTimeEnd').text  # type: ignore [reportOptionalMemberAccess]
        return subtract_time(init_time, final_time)
    except AttributeError:
        return ""


def get_chapter_string(chapter: bs4.element.Tag) -> str:
    """Parse an appropriate title for the chapter."""
    try:
        return chapter.find('ChapterString').text  # type: ignore [reportOptionalMemberAccess]
    except AttributeError:
        return f"Chapter {chapter.find('ChapterUID')}"


if __name__ == "__main__":
    with open(sys.argv[1], 'r') as xml_file:
        chapters_xml = bs4.BeautifulSoup(xml_file.read(), 'xml')

    chapters = chapters_xml.find_all('ChapterAtom')

    for chapter_num, chapter_data in enumerate(chapters, 1):
        print(
            f"{chapter_num}. "
            f"{get_chapter_string(chapter_data)} "
            f"({get_chapter_time(chapter_data)})"
        )
