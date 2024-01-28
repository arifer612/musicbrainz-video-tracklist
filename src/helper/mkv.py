### mkv.py
## Library of tools of manipulating mkv files

import bs4
import os


def mkv__read_file(file_path: str) -> list[bs4.element.Tag]:
    """Read the chapter file."""
    if os.path.splitext(file_path)[1] != ".xml":
        raise AttributeError("MKV chapters should be XML files.")
    with open(file_path, 'r') as xml_file:
        chapters_xml = bs4.BeautifulSoup(xml_file.read(), 'xml')
        return chapters_xml.find_all('ChapterAtom')


def mkv__get_chapter_time(chapter: bs4.element.Tag) -> tuple[str, str]:
    """Read the chapter and get the initial and final timestamps."""
    try:
        init_time = chapter.find('ChapterTimeStart').text  # type: ignore [reportOptionalMemberAccess]
        final_time = chapter.find('ChapterTimeEnd').text  # type: ignore [reportOptionalMemberAccess]
        return (init_time[:-3], final_time[:-3])
    except AttributeError:
        return ("", "")


def mkv__get_chapter_string(chapter: bs4.element.Tag) -> str:
    """Parse an appropriate title for the chapter."""
    try:
        return chapter.find('ChapterString').text  # type: ignore [reportOptionalMemberAccess]
    except AttributeError:
        return f"Chapter {chapter.find('ChapterUID')}"
