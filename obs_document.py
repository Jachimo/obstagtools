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

    def detect_frontmatter(self):
        """Try to detect beginning of frontmatter, end of frontmatter, and tags line"""
        if self.lines[0] == '---\n':
            self.frontmatterstart = 0
            logging.debug(f'Start of frontmatter found at line {self.frontmatterstart}')
        for i in range(1, len(self.lines)):
            if self.lines[i] == 'tags:\n':  # Note: there _are_ other valid YAML ways to do tags, but not supported here
                self.tagline = i
                logging.debug(f'Likely "tag:" line found at line {self.tagline}')
            if self.lines[i] == '---\n':
                self.frontmatterend = i
                logging.debug(f'Likely end of frontmatter found at line {self.frontmatterend}')

    def validate_structure(self) -> bool:
        """Test and ensure that self.lines has content, and frontmatterstart, frontmatterend, and tagline are set"""
        if len(self.lines) <= 1:
            logging.debug('No lines found')
            return False
        if not self.frontmatterstart:
            logging.debug('frontmatterstart is not defined')
            return False
        if not self.frontmatterend:
            logging.debug('frontmatterend is not defined')
            return False
        if not self.tagline:
            logging.debug('tagline is not defined')
            return False
        if self.frontmatterend <= self.tagline:
            logging.debug('frontmatterend is before tagline, which should not happen')
            return False
        else:
            return True

    def add_tag(self, tag: str):
        """Adds specified tag to the document frontmatter"""
        if not self.validate_structure():
            self.detect_frontmatter()
            if not self.validate_structure():
                raise ValueError(f'{self.filename} failed structure validation')
        self.lines.insert(self.tagline+1, '  - ' + tag.strip() + '\n')

    def get_frontmatter(self) -> ['']:
        """Retrieve list of strings containing lines in the frontmatter (YAML) part of the file"""
        if not self.validate_structure():
            self.detect_frontmatter()
            if not self.validate_structure():
                raise ValueError(f'{self.filename} failed structure validation')
        return self.lines[self.frontmatterstart:self.frontmatterend+1]
