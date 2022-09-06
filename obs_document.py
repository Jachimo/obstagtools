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
            if self.lines[i] == 'tags:\n':  # Only block-style YAML, not flow, is supported for tags
                self.tagline = i
                logging.debug(f'Likely "tag:" line found at line {self.tagline}')
            if self.lines[i] == '---\n':
                self.frontmatterend = i
                logging.debug(f'Likely end of frontmatter found at line {self.frontmatterend}')

    def validate_structure(self) -> bool:
        """Test and ensure that self.lines has content, and frontmatterstart, frontmatterend, and tagline are set"""
        if len(self.lines) <= 3:
            logging.debug('Not enough lines found')
            return False
        if self.frontmatterstart is None:  # N.B.: 0 (zero) is a valid and common value for frontmatterstart!
            logging.debug('frontmatterstart is not defined')
            return False
        if self.frontmatterend is None:
            logging.debug('frontmatterend is not defined')
            return False
        if self.tagline is None:
            logging.debug('tagline is not defined')
            return False
        if self.frontmatterend <= self.tagline:
            logging.debug('frontmatterend is before tagline, which should not happen')
            return False
        else:
            return True

    def validate(self, try_redetect=True) -> bool:
        """Run validation(s) on the document and return True if passed, False if failed.
        The try_redetect= option re-runs detect_frontmatter() if validation fails, then
        re-tries validation before giving a final result.
        """
        if try_redetect:  # try_redetect= if validation fails, re-run detect_frontmatter() and try again
            if self.validate_structure():
                return True
            else:
                self.detect_frontmatter()
                if self.validate_structure():
                    return True
                else:
                    return False
        else:
            if self.validate_structure():
                return True
            else:
                return False

    def add_tag(self, tag: str):
        """Adds specified tag to the document frontmatter"""
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        self.lines.insert(self.tagline + 1, '  - ' + tag.strip() + '\n')  # assumes (sequence=4, offset=1) indents?

    def get_frontmatter(self) -> str:
        """Retrieve the YAML frontmatter section as a string.
        Output format is designed to match input requirements of yaml.safe_load()
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        return ''.join(self.lines[self.frontmatterstart:self.frontmatterend])

    def replace_frontmatter(self, newfmlines: ['']):
        """Replace the existing frontmatter (in self.lines) with the supplied
        list of strings, and re-run detect_frontmatter() to update properties
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        newlines: [''] = newfmlines + self.lines[self.frontmatterend:]
        self.lines = newlines
        self.detect_frontmatter()

    def get_content(self) -> ['']:
        """Retrieve the Markdown-formatted content, which is the rest of the
        document after the end of the frontmatter.  Return a list of strings.
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        return self.lines[self.frontmatterend:]

    def set_content(self, newcontentlines: ['']):
        """Replace the existing content (in self.lines) with the supplied
        list of strings
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        newlines: [''] = self.lines[:self.frontmatterend] + newcontentlines
        self.lines = newlines

    def wikify_terms(self, termslist: ['']):
        """Make *all* occurrences of each of the list of terms into
        an internal wiki-type link, by enclosing in [[double brackets]]
        """
        newcontent: [''] = []
        for line in self.get_content():
            newline: str = line
            for term in termslist:
                newline = newline.replace(term, '[[' + term + ']]')
            newcontent.append(newline)
        self.set_content(newcontent)
