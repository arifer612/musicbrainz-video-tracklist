#!/usr/bin/env python
### chaps-to-mb
## Parse a chapter file into a tracklist for MusicBrainz

import sys
from src import read_and_print


if __name__ == "__main__":
    read_and_print(sys.argv[1])
