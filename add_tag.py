#!/usr/bin/env python3
import argparse
import logging
import sys

import obs_document


def main() -> int:  # returns Unix exit value
    parser = argparse.ArgumentParser(description='Add YAML frontmatter tags to Obsidian-style Markdown files')
    parser.add_argument('inpath', help='Input file to add tags to')
    parser.add_argument('outpath', nargs='?', default=False,
                        help='Output file to write to (in-place modification if not given)')
    parser.add_argument('--tag', '-t', nargs='+', help='Tag values to add to the document')
    parser.add_argument('--debug', help='Enable debug mode (verbose output)', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug output enabled')
    else:
        logging.basicConfig(level=logging.INFO)

    if not args.tag:
        logging.info('No tag(s) specified, exiting')
        return 1

    if not args.outpath:
        logging.debug('No output path specified, performing in-place modification')
        args.outpath = args.inpath

    obsdoc: obs_document.ObsDocument
    obsdoc = obs_document.ObsDocument()  # see obs_document.py

    logging.debug(f'Reading from {args.inpath}')
    with open(args.inpath, 'r') as infile:
        obsdoc.filename = args.inpath
        obsdoc.lines = infile.readlines()
        logging.debug(f'Read {len(obsdoc.lines)} lines')

    t: str
    for t in args.tag:
        obsdoc.add_tag(t)

    logging.debug(f'Writing to {args.outpath}')
    with open(args.outpath, 'w') as outfile:
        outfile.writelines(obsdoc.lines)
        logging.debug(f'Wrote {len(obsdoc.lines)} lines')

    logging.debug('Exiting successfully')
    return 0


if __name__ == '__main__':
    sys.exit(main())
