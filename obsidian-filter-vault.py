# /usr/bin/env python3
# obsidian-filter-vault.py
# Filters an Obsidian "Vault" based on document metadata
# Requires Python 3.5+, tested using Python 3.9
import sys
import argparse
import logging
import os
from typing import List
import oyaml as yaml
import pathlib
import shutil

import obs_document


ALLOWED_FILE_EXTENSIONS: List[str] = ['md', 'markdown', 'mdown', 'mdkn', 'obs']  # edit as needed, e.g. for .txt


def main() -> int:
    parser = argparse.ArgumentParser(description='Filter an Obsidian vault based on document metadata')
    parser.add_argument('inpath', help='Source vault path')
    parser.add_argument('outpath', help='Destination path')
    parser.add_argument('command', type=str, choices={'COPY', 'copy', 'MOVE', 'move'},
                        help='Command to execute (see -h for possible commands)')
    parser.add_argument('filterfield', help='Metadata field to filter by (e.g. "tags")')
    parser.add_argument('operation', type=str, choices={'INCLUDE', 'include', 'EXCLUDE', 'exclude'},
                        help='Whether output must INCLUDE or EXCLUDE the specified field value from output set')
    parser.add_argument('fieldvalue', help='Field value (e.g. "books")')
    parser.add_argument('--force', action='store_true',
                        help='Perform operation even if outpath is not empty (WARNING: will overwrite files!')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (verbose output)')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug output enabled')
    else:
        logging.basicConfig(level=logging.INFO)

    # Input sanity checks
    if os.path.isdir(args.outpath):
        if len(os.listdir(args.outpath)) != 0:
            if not args.force:
                logging.info(f'Destination directory {args.outpath} is not empty and --force not specified; aborting.')
                return 1
    if not os.path.isdir(args.inpath):
        logging.info('Input path must refer to a directory.')
        return 1

    # Build list of files to filter, based on extension
    filelist: List[str] = []
    for root, dirs, files in os.walk(args.inpath):
        for f in files:
            if f.split('.')[-1] in ALLOWED_FILE_EXTENSIONS:
                filelist.append(f'{root}{os.sep}{f}')
    logging.debug(f'Unfiltered filelist contains {len(filelist)} items')

    # Convert the user-supplied string to the proper datatype
    filterfieldvalue = yaml.safe_load(args.fieldvalue)
    logging.debug(f'Filter field value is {filterfieldvalue} (type {type(filterfieldvalue)})')

    # Inspect each file and prune filelist as appropriate
    for fp in filelist:
        obsdoc = obs_document.ObsDocument(fp)
        metadata: dict = yaml.safe_load(obsdoc.get_frontmatter_str())
        logging.debug(f'{fp} metadata parsed as:\n{metadata}')

        # If operation == INCLUDE, means MUST CONTAIN OR MATCH specified filterfieldvalue
        if args.operation in ['INCLUDE', 'include']:
            if args.filterfield in metadata:
                if type(metadata[args.filterfield]) is list:  # Handle case where the value on the doc is a list
                    if filterfieldvalue in metadata[args.filterfield]:
                        continue
                    else:
                        filelist.remove(fp)
                if type(metadata[args.filterfield]) in [str, bool, float, int]:  # Handle single-value cases
                    if filterfieldvalue == metadata[args.filterfield]:
                        continue
                    else:
                        filelist.remove(fp)
                if type(metadata[args.filterfield]) is dict:
                    # TODO: handle dict-type fields on document
                    logging.info(f'Matching against dictionary is not currently supported; skipping {fp}')
                    filelist.remove(fp)
            else:
                filelist.remove(fp)

        # If operation == EXCLUDE, means filterfield MUST NOT CONTAIN OR MATCH specified filterfieldvalue
        if args.operation in ['EXCLUDE', 'exclude']:
            if args.filterfield in metadata:
                if type(metadata[args.filterfield]) is list:
                    if filterfieldvalue in metadata[args.filterfield]:
                        filelist.remove(fp)
                if type(metadata[args.filterfield]) in [str, bool, float, int]:
                    if filterfieldvalue == metadata[args.filterfield]:
                        filelist.remove(fp)
                if type(metadata[args.filterfield]) is dict:
                    # TODO: handle dict-type fields on document
                    logging.info(f'Matching against dictionary is not currently supported; skipping {fp}')
                    filelist.remove(fp)
            else:
                continue
    logging.debug(f'Filtered filelist now contains {len(filelist)} items')

    # Do something (move, copy) to the files on the list
    for fp in filelist:
        newfp = f'{args.outpath.strip(os.sep)}{os.sep}{fp.strip(os.sep).split(os.sep, 1)[-1]}'
        pathlib.Path(os.path.dirname(newfp)).mkdir(parents=True, exist_ok=True)  # create dir tree if needed
        if args.command in ['COPY', 'copy']:
            logging.debug(f'Copying from {fp} to {newfp}')
            shutil.copy(fp, newfp)
        if args.command in ['MOVE', 'move']:
            logging.info('Command "move" is not yet implemented, sorry.')
            pass

    return 0  # success


if __name__ == '__main__':
    sys.exit(main())
