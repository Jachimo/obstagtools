# Part of 'Obsidian Tag Tools': https://github.com/Jachimo/obstagtools
# Requires Python 3.5+, tested using Python 3.9

import logging
import re
from typing import Optional, List, Iterable, Type

import obs_config as config


# LOGGING
logger = logging.getLogger(__name__)


# Utility functions
def check_inner_type(iterable: Iterable, tp: Type) -> bool:
    """Check inner types of a nested object, e.g. list of strings

    Args:
        iterable: iterable 'outer' object
        tp: desired type of each 'inner' object

    Returns:
        True if all 'inner' objects are of type tp
        False if any are not
    """
    return all(isinstance(i, tp) for i in iterable)


class ObsDocument(object):
    def __init__(self, inputfilename: str):
        """Initialize an Obsidian Document object

        Args:
            inputfilename: path to a valid Obsidian .md file
        """
        logger.debug(f'Parsing: {inputfilename}')
        self.filename: str = inputfilename

        with open(self.filename, 'r') as f:
            self.lines: List[str] = f.readlines()
        self._frontmatterstart: Optional[int] = None  # line index of first "---\n"
        self._frontmatterend: Optional[int] = None  # line index of second "---\n"
        self._tagline: Optional[int] = None  # line index of "tags:\n"
        self.metadata = {}
        self.detect_frontmatter()

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, fn: str) -> None:
        if not fn:
            raise ValueError(f'Filename must have a non-False string value.')
        self._filename = fn

    @property
    def frontmatter(self) -> List[str]:
        """Get YAML frontmatter section as list of strings.

        Returns:
            A list of strings, one string per line with '\n' terminators
            included, similar to the output of file.readlines().
        """
        return self.lines[self._frontmatterstart:self._frontmatterend]

    @frontmatter.setter
    def frontmatter(self, newfmlines: List[str]) -> None:
        """Set the document's frontmatter.

        Args:
            newfmlines: A list of strings, containing the new frontmatter section.
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        if not check_inner_type(newfmlines, str):
            raise TypeError(f'Frontmatter must be set to a list of strings')
        newlines: List[str] = newfmlines + self.lines[self._frontmatterend:]
        self.lines = newlines
        self.detect_frontmatter()

    @property
    def frontmatter_str(self) -> str:
        """Retrieve the YAML frontmatter section as a string.

        Returns:
            A string, meant to match input requirements of yaml.safe_load().
        """
        return ''.join(self.frontmatter)

    @property
    def content(self) -> List[str]:
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

    @content.setter
    def content(self, newcontentlines: List[str]) -> None:
        """Replace the document content.

        Args:
            newcontentlines: list of strings containing the new content.
        """
        if not self.validate():
            raise ValueError(f'{self.filename} failed structure validation')
        if not check_inner_type(newcontentlines, str):
            raise TypeError(f'Content must be set to a list of strings')
        newlines: List[str] = self.lines[:self._frontmatterend] + newcontentlines
        self.lines = newlines

    @property
    def metadata(self) -> dict:
        return self._metadata

    @metadata.setter
    def metadata(self, newmd: dict) -> None:
        if type(newmd) is not dict:
            raise TypeError('Document metadata must be a dictionary.')
        self._metadata = newmd

    @property
    def internal_links(self) -> List[str]:
        """Get a list of [[internal link]] targets extracted from the document.

        Internal links are only those enclosed in double brackets,
        and targets are extracted using a regular expression (config.LINK_REGEXP) which
        very likely errs on the side of false-positives.

        If a link contains an optional component delimited with a pipe character,
        such as [[my_image.jpg|500]], only "my_image.jpg" is extracted.

        Returns:
            List of strings from inside [[double bracketed]] links.
        """
        return re.findall(config.LINK_REGEXP, ''.join(self.lines))

    def detect_frontmatter(self) -> None:
        """Try to detect beginning of frontmatter, end of frontmatter, and tags line
        """
        if self.lines[0] == '---\n':
            self._frontmatterstart = 0
            logger.debug(f'Start of frontmatter found at line {self._frontmatterstart}')
        for i in range(1, len(self.lines)):
            if self.lines[i] == 'tags:\n':  # Only block-style YAML, not flow, is supported for tags
                self._tagline = i
                logger.debug(f'Likely "tag:" line found at line {self._tagline}')
            if self.lines[i] == '---\n':
                self._frontmatterend = i
                logger.debug(f'Likely end of frontmatter found at line {self._frontmatterend}')

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
            logger.debug('Not enough lines found')
            return False
        if self._frontmatterstart is None:  # N.B.: 0 (zero) is a valid and common value for frontmatterstart!
            logger.debug('frontmatter start is not defined')
            return False
        if self._frontmatterend is None:
            logger.debug('frontmatter end is not defined')
            return False
        if self._tagline is None:
            logger.debug('tag line is not defined')
            return False
        if self._frontmatterend <= self._tagline:
            logger.debug('frontmatter end is before tag line, which should not happen')
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
        assert self._tagline is not None
        self.lines.insert(self._tagline + 1, '  - ' + tag.strip() + '\n')  #

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
        for line in self.content:
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
        self.content = newcontent
