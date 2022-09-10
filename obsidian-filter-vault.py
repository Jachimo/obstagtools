# /usr/bin/env python3
# obsidian-filter-vault.py
# Filters an Obsidian "Vault" based on document metadata
import sys
import argparse
import logging
import os
from typing import List
import oyaml as yaml

import obs_document

def main() -> int:
    parser = argparse.ArgumentParser(description='Filter an Obsidian vault based on document metadata')
    parser.add_argument('inpath', help='Source vault path')
    parser.add_argument('outpath', nargs='?', default=False, help='Destination path')
    parser.add_argument('command', help='Command to execute (type of operation to perform)')
    parser.add_argument('filterfield', help='Metadata field to filter by (e.g. "tags")')
    parser.add_argument('fieldvalue', help='Field value: prefix with "+" to require, "-" to exclude (e.g. "+books")')
    parser.add_argument('--debug', help='Enable debug mode (verbose output)', action='store_true')
    args = parser.parse_args()

    commandlist: List[str] = ['copymatches', 'movematches']  # add others here as they are implemented
    allowedextensions: List[str] = ['md', 'markdown', 'mdown', 'mdkn', 'obs']

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug output enabled')
    else:
        logging.basicConfig(level=logging.INFO)

    # Input sanity checks
    if not args.inpath or not args.command or not args.filterfield or not args.fieldvalue:
        logging.info('Missing one or more required arguments; exiting.')
        return 1
    if args.command not in commandlist:
        logging.info(f'Unrecognized command entered: {args.command}\n'
                     f'Valid commands are: {commandlist}')
        return 1
    if args.fieldvalue[0] not in ['+', '-']:
        logging.info('Field value must be prefixed by a "+" or "-" to include or exclude.\n'
                     f'Value entered: {args.fieldvalue}')
        return 1
    if not args.outpath:
        logging.info('No output location specified.')
        return 1  # For in-place modification, this rule would need to be modified, and outpath=inpath
    if not os.path.isdir(args.inpath):
        logging.info('Input path must refer to a directory.')
        return 1

    # Build list of files to filter, based on extension
    filelist: List[str] = []
    for root, dirs, files in os.walk(args.inpath):
        for f in files:
            if f.split('.')[-1] in allowedextensions:
                filelist.append(f'{root}{os.sep}{f}')
    logging.debug(f'Filelist is: {filelist}')

    # Inspect and try to decode each file (try... around the initial parsing, and log errors?)
    for fp in filelist:
        logging.debug(f'Attempting to parse {fp}')
        obsdoc = obs_document.ObsDocument(fp)
        metadata: dict = yaml.safe_load(obsdoc.get_frontmatter_str())
        logging.debug(f'Frontmatter YAML parsed as:\n{metadata}')

    # Remove files that do not match criteria from list

    # Do something (move, copy) the remaining files on the list

    return 0


if __name__ == '__main__':
    sys.exit(main())
