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

    # Set up logging
    rootlogger = logging.getLogger()
    logger = logging.getLogger(__name__)
    log_format: str = "[%(filename)20s,%(lineno)3s:%(funcName)20s] %(message)s"
    logging.basicConfig(format=log_format)
    if args.debug:
        rootlogger.setLevel(logging.DEBUG)
        logger.debug('Debug output enabled')
    else:
        rootlogger.setLevel(logging.INFO)

    if not args.tag:
        logger.info('No tag(s) specified, exiting')
        return 0
    if not args.outpath:
        logger.debug('No output path specified, performing in-place modification')
        args.outpath = args.inpath

    obsdoc: obs_document.ObsDocument
    obsdoc = obs_document.ObsDocument(args.inpath)  # see obs_document.py

    t: str
    for t in reversed(args.tag):
        obsdoc.add_tag(t)

    logger.debug(f'Writing to {args.outpath}')
    with open(args.outpath, 'w') as outfile:
        outfile.writelines(obsdoc.lines)
        logger.debug(f'Wrote {len(obsdoc.lines)} lines')

    logger.debug('Exiting successfully')
    return 0


if __name__ == '__main__':
    sys.exit(main())
