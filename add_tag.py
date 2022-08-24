#!/usr/bin/env python3
import argparse
import logging
import sys

import obs_document


def main() -> int:  # returns Unix exit value
    parser = argparse.ArgumentParser(description='Add YAML frontmatter tags to Obsidian-style Markdown files')
    parser.add_argument('inpath', help='Input file to add tags to')
    parser.add_argument('outpath', nargs='?', default=False, help='Output file to write to (in-place modification if not given)')
    parser.add_argument('--tag', '-t', nargs='+', help='Tag values to add to the document')  # TODO: should support multiple tags
    parser.add_argument('--debug', help='Enable debug mode (very verbose output)', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug output enabled')
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug(f'Reading from {args.inpath}')

    if not args.tag:
        logging.info('No tag(s) specified, exiting')
        return 1

    if not args.outpath:
        logging.info('WARNING: No output path specified, performing in-place modification')
        args.outpath = args.inpath

    obsdoc = obs_document.ObsDocument()  # see obs_document.py

    with open(args.inpath, 'r') as infile:
        obsdoc.lines = infile.readlines()
        logging.debug(f'Read {len(obsdoc.lines)} lines')

    for t in args.tag:
        add_tag(obsdoc, t)

    with open(args.outpath, 'w') as outfile:
        logging.debug(f'Writing to {args.outpath}')
        outfile.writelines(obsdoc.lines)
        logging.debug(f'Wrote {len(obsdoc.lines)}')

    return 0


def add_tag(doc: obs_document.ObsDocument, tag: str) -> obs_document.ObsDocument:
    """Adds specified tag to the lines contained in the ObsDocument object"""

    if not doc.isWellFormed():
        logging.debug('Input file does not appear to begin with well-formed YAML, exiting')
        raise ValueError

    newtagstr: str = '  - ' + tag.strip() + '\n'  # Note we are using two spaces, a dash -, a space, and the value

    newlines: [str] = doc.lines[doc.frontmatterstart:(doc.tagline+1)]
    newlines.append(newtagstr)
    newlines.extend(doc.lines[(doc.tagline+1):])

    doc.lines = newlines
    return doc


if __name__ == '__main__':
    sys.exit(main())
