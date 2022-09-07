# Class for working with Obsidian-flavor Markdown+YAML documents
import logging
from typing import Optional, List


class ObsDocument(object):
    def __init__(self, filename: str):
        """Initialize an ObsDocument object

        Args:
            filename: path to a valid Obsidian .md file
        """
        self.filename: str = filename
        with open(self.filename, 'r') as f:
            self.lines: List[str] = f.readlines()
        self._frontmatterstart: Optional[int] = None  # line index of first "---\n"
        self._frontmatterend: Optional[int] = None  # line index of second "---\n"
        self._tagline: Optional[int] = None  # line index of "tags:\n"
        self.detect_frontmatter()

    def detect_frontmatter(self) -> None:
        """Try to detect beginning of frontmatter, end of frontmatter, and tags line
        """
        if self.lines[0] == '---\n':
            self._frontmatterstart = 0
            logging.debug(f'Start of frontmatter found at line {self._frontmatterstart}')
        for i in range(1, len(self.lines)):
            if self.lines[i] == 'tags:\n':  # Only block-style YAML, not flow, is supported for tags
                self._tagline = i
                logging.debug(f'Likely "tag:" line found at line {self._tagline}')
            if self.lines[i] == '---\n':
                self._frontmatterend = i
                logging.debug(f'Likely end of frontmatter found at line {self._frontmatterend}')

    def validate_structure(self) -> bool:
        """Check whether important properties have been set

        The overall goal is to test for well-formedness by validating:
         - That self.lines has content;
         - frontmatterstart is not None;
         - tagline is not None;
         - frontmatterend is not None;
         - frontmatterend > tagline (i.e. tagline is inside the frontmatter)

        Returns:
            True if document has passed all validation checks.
            False if any validation checks have failed.
        """
        if len(self.lines) <= 3:
            logging.debug('Not enough lines found')
            return False
        if self._frontmatterstart is None:  # N.B.: 0 (zero) is a valid and common value for frontmatterstart!
            logging.debug('frontmatter start is not defined')
            return False
        if self._frontmatterend is None:
            logging.debug('frontmatter end is not defined')
            return False
        if self._tagline is None:
            logging.debug('tag line is not defined')
            return False
        if self._frontmatterend <= self._tagline:
            logging.debug('frontmatter end is before tag line, which should not happen')
            return False
        else:
            return True

    def validate(self, try_redetect: bool = True) -> bool:
        """Run self-checks on the document and return True if they pass.

        Args:
            try_redetect: If True, call detect_frontmatter() and retry
              validation one time, before failing. Defaults to True.
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

    def add_tag(self, tag: str) -> None:
        """Adds specified tag to the document frontmatter.

        Args:
            tag: string value of the tag to be added.

        Raises:
            ValueError: structure validation failed, some properties were invalid.
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        self.lines.insert(self._tagline + 1, '  - ' + tag.strip() + '\n')  # assumes (sequence=4, offset=1) indents?

    def get_frontmatter(self) -> List[str]:
        """Retrieve YAML frontmatter section as list of strings.

        Returns:
            A list of strings, one string per line with '\n' terminators
            included, similar to the output of file.readlines().
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        return self.lines[self._frontmatterstart:self._frontmatterend]

    def get_frontmatter_str(self) -> str:
        """Retrieve the YAML frontmatter section as a string.

        Returns:
            A string, meant to match input requirements of yaml.safe_load().
        """
        return ''.join(self.get_frontmatter())

    def set_frontmatter(self, newfmlines: List[str]) -> None:
        """Replace the document's frontmatter.

        Args:
            newfmlines: A list of strings, containing the new frontmatter section.
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        newlines: List[str] = newfmlines + self.lines[self._frontmatterend:]
        self.lines = newlines
        self.detect_frontmatter()

    def get_content(self) -> List[str]:
        """Retrieve the Markdown-formatted content.

        The 'content' is the rest of the document AFTER the end of the frontmatter,
        i.e. the part that's formatted with Markdown and is usually supplied by
        the user.

        Returns:
            A list of strings.
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        return self.lines[self._frontmatterend:]

    def set_content(self, newcontentlines: List[str]) -> None:
        """Replace the document content.

        Args:
            newcontentlines: list of strings containing the new content.
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        newlines: List[str] = self.lines[:self._frontmatterend] + newcontentlines
        self.lines = newlines

    def wikify_terms(self,
                     termslist: list,
                     firstonly: bool = False,
                     skipheaders: bool = False) -> None:
        """Wikify supplied terms by placing them in [[brackets]].

        Default behavior is to place brackets around *every* occurrence
        of each term in the supplied list, throughout the entire doc content.

        Args:
            termslist: list of strings containing the terms to be linked.
            firstonly: if True, only wikify the first occurrence of the term (default False)
            skipheaders: if True, lines starting with '#' will not be wikified (default False)
        """
        newcontent: List[str] = []
        line: str
        for line in self.get_content():
            if skipheaders:
                if line[0] == '#':
                    newcontent.append(line)
                    continue
            newline: str = line
            term: str
            for term in termslist:
                if term in line:
                    if firstonly:
                        newline = newline.replace(term, '[[' + term + ']]', 1)
                        termslist.remove(term)
                    else:
                        newline = newline.replace(term, '[[' + term + ']]')
            newcontent.append(newline)
        self.set_content(newcontent)
