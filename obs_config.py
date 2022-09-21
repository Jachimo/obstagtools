# Configuration File for `obstagtools`
# Part of 'Obsidian Tag Tools': https://github.com/Jachimo/obstagtools
# Requires Python 3.5+, tested using Python 3.9

import re
from typing import List

# Regular expression to use for detecting [[internal links]] within Obsidian docs
#  See https://regex101.com/r/kEmr3g/2
LINK_REGEXP: re.Pattern = re.compile(r'\[\[(.{4,}?)(?:\||\]\])', re.MULTILINE)

# Both SKIP_DIRS and ATTACHMENT_DIRS are relative to the vault root
#  SKIP_DIRS are completely ignored, they are neither searched for notes or copied to output
SKIP_DIRS: List[str] = ['Templates', '.obsidian']
#  ATTACHMENT_DIRS content is copied under some circumstances
ATTACHMENT_DIRS: List[str] = ['Attachments']

# Only files with one of the ALLOWED_FILE_EXTENSIONS are considered possible Obsidian notes
ALLOWED_FILE_EXTENSIONS: List[str] = ['md', 'markdown', 'mdown', 'mkdn', 'obs']

# Test data directory (used by pytest unit tests)
TEST_DATA_DIR = 'testdata/'
