#!/usr/bin/env python
"""Parse a chapter file into a tracklist for MusicBrainz."""

import sys
from src import print_chapters


if __name__ == "__main__":
    print_chapters(sys.argv[1])
