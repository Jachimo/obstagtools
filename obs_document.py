# Class for working with Obsidian-flavor Markdown+YAML documents
import logging


class ObsDocument:
    """Basic class for representing Obsidian documents, aka notes"""
    def __init__(self):
        self.filename: str = ''
        self.lines: [str] = ['']
        self.frontmatterstart: int = None  # line index of first "---\n"
        self.frontmatterend: int = None  # line index of second "---\n"
        self.tagline: int = None  # line index of "tags:\n"

    def isWellFormed(self) -> bool:
        """Test self.lines to see if it starts with reasonably well-formed YAML header and tags line"""
        if self.lines[0] == '---\n':
            self.frontmatterstart = 0
        else:
            logging.debug('File does not begin with "---<LF>"')
            return False  # For now, only handle files with YAML at beginning...

        for i in range(1, len(self.lines)):
            if self.lines[i] == 'tags:\n':  # Note: there _are_ other valid YAML ways to do tags, but not supported here
                self.tagline = i
                logging.debug(f'Likely "tag:" line found at {self.tagline}')
            if self.lines[i] == '---\n':
                self.frontmatterend = i
                logging.debug(f'End of YAML frontmatter found at {self.frontmatterend}')

        if not self.frontmatterend:
            logging.debug('File appears to be missing YAML end marker')
            return False
        if not self.tagline:
            logging.debug('File appears to be missing "tag:" line in YAML')
            # TODO: handle this case by adding a "tag:\n" line
            return False
        if self.frontmatterend <= self.tagline:
            logging.debug('YAML end marker found before "tag:", which should not happen')
            return False

        return True
