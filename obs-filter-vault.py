#!/usr/bin/env python3

# obsidian-filter-vault.py
#  Filters an Obsidian "Vault" based on document metadata
#  Requires Python 3.5+, tested using Python 3.9

import sys
import argparse
import logging
import os
from typing import List, Any
import oyaml as yaml
import pathlib
import shutil

import obs_document


SKIP_DIRS: List[str] = ['Templates', '.obsidian']
ATTACHMENT_DIRS: List[str] = ['Attachments']
ALLOWED_FILE_EXTENSIONS: List[str] = ['md', 'markdown', 'mdown', 'mkdn', 'obs']  # edit as needed, e.g. for .txt


def main() -> int:
    parser = argparse.ArgumentParser(description='Filter an Obsidian vault based on document metadata')
    parser.add_argument('inpath', help='Source vault path')
    parser.add_argument('outpath', help='Destination path (must be empty unless --force is used)')
    parser.add_argument('command', type=str.upper, choices={'COPY', 'MOVE'},
                        help='Command to execute')
    parser.add_argument('filterfield', help='Metadata field to filter by (e.g. "tags")')
    parser.add_argument('operation', type=str.upper, choices={'INCLUDE', 'EXCLUDE'},
                        help='Whether output must INCLUDE or EXCLUDE the specified field value from output set')
    parser.add_argument('fieldvalue', help='Field value (e.g. "personal")')
    parser.add_argument('--force', action='store_true',
                        help='Perform operation even if outpath is not empty (WARNING: will clobber!)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (verbose output)')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug output enabled')
    else:
        logging.basicConfig(level=logging.INFO)

    # Input sanity checks
    if not os.path.isdir(args.inpath):
        logging.info('Input path must refer to a directory.')
        return 1
    if os.path.isdir(args.outpath):
        if len(os.listdir(args.outpath)) != 0:
            if not args.force:
                logging.info(f'Destination directory {args.outpath} is not empty and --force not specified; aborting.')
                return 1

    # Build list of files to filter, based on extension
    filelist: List[str] = []
    for root, dirs, files in os.walk(args.inpath):
        for f in files:
            if any(s in root for s in SKIP_DIRS):  # don't add files from SKIP_DIRS
                continue
            elif any(s in root for s in ATTACHMENT_DIRS):  # or ATTACHMENT_DIRS
                continue
            elif f.split('.')[-1] in ALLOWED_FILE_EXTENSIONS:  # see top of file
                filelist.append(f'{root}{os.sep}{f}')
    logging.debug(f'Unfiltered filelist contains {len(filelist)} items: {filelist}')

    # Convert the user-supplied string to the proper datatype
    filterfieldvalue: Any = yaml.safe_load(args.fieldvalue)
    logging.debug(f'Operation will {args.operation} '
                  f'if {args.filterfield} '
                  f'matches {filterfieldvalue} '
                  f'(type {type(filterfieldvalue)})')

    # Inspect each file and create outputlist as appropriate
    outputlist: List[str] = []
    for fp in filelist:
        logging.debug(f'Parsing: {fp}')
        obsdoc: obs_document.ObsDocument = obs_document.ObsDocument(fp)
        metadata: dict = yaml.safe_load(obsdoc.get_frontmatter_str())
        #logging.debug(f'{fp} metadata parsed as:\n{metadata}')

        # If operation == INCLUDE...
        if args.operation in ['INCLUDE', 'include']:
            if args.filterfield in metadata:
                if type(metadata[args.filterfield]) is list:
                    if filterfieldvalue in metadata[args.filterfield]:
                        outputlist.append(fp)
                elif type(metadata[args.filterfield]) in [str, bool, float, int]:
                    if filterfieldvalue == metadata[args.filterfield]:
                        outputlist.append(fp)
                elif type(metadata[args.filterfield]) is dict:
                    if filterfieldvalue == metadata[args.filterfield]:  # May want to consider special handling here
                        outputlist.append(fp)
                else:
                    raise ValueError(f'Unknown datatype in {fp.strip(os.sep).split(os.sep)[-1]}, '
                                     f'field {args.filterfield}, '
                                     f'value {metadata[args.filterfield]}, '
                                     f'type {type(metadata[args.filterfield])}')
            else:
                logging.debug(f'Field {args.filterfield} not found in doc {fp}; not including in output')
                continue

        # If operation == EXCLUDE...
        if args.operation in ['EXCLUDE', 'exclude']:
            if args.filterfield in metadata:
                #logging.debug(f'Field {args.filterfield} (value {metadata[args.filterfield]}, type {type(metadata[args.filterfield])}) found in doc {fp}')
                if type(metadata[args.filterfield]) is list:
                    if filterfieldvalue in metadata[args.filterfield]:
                        continue
                    else:
                        outputlist.append(fp)
                elif type(metadata[args.filterfield]) in [str, bool, float, int]:
                    if filterfieldvalue == metadata[args.filterfield]:
                        continue
                    else:
                        outputlist.append(fp)
                elif type(metadata[args.filterfield]) is dict:
                    if filterfieldvalue == metadata[args.filterfield]:  # May want to consider special handling here
                        continue
                else:
                    raise ValueError(f'Unknown datatype in {fp.strip(os.sep).split(os.sep)[-1]}, '
                                     f'field {args.filterfield}, '
                                     f'value {metadata[args.filterfield]}, '
                                     f'type {type(metadata[args.filterfield])}')
            else:
                logging.debug(f'Field {args.filterfield} not found in doc {fp}; appending to output')
                outputlist.append(fp)

    logging.debug(f'Filtered filelist now contains {len(outputlist)} items')

    # Do something (move, copy) with the files on the list
    for fp in outputlist:
        newfp = f'{args.outpath.strip(os.sep)}{os.sep}{fp.strip(os.sep).split(os.sep, 1)[-1]}'
        pathlib.Path(os.path.dirname(newfp)).mkdir(parents=True, exist_ok=True)  # create dir tree if needed
        if args.command in ['COPY', 'copy']:
            logging.debug(f'Copying: {fp} -> {newfp}')
            shutil.copy(fp, newfp)
        if args.command in ['MOVE', 'move']:
            logging.debug(f'Moving: {fp} -> {newfp}')
            shutil.move(fp, newfp)

    return 0  # success


if __name__ == '__main__':
    sys.exit(main())
