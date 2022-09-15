#!/usr/bin/env python3

# obs-filter-vault.py
#  Filters an Obsidian "Vault" based on document metadata
#  Part of 'Obsidian Tag Tools': https://github.com/Jachimo/obstagtools
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

# Both SKIP_DIRS and ATTACHMENT_DIRS are excluded from the search for Obsidian notes files
SKIP_DIRS: List[str] = ['Templates', '.obsidian']
ATTACHMENT_DIRS: List[str] = ['Attachments']

# Only files with one of the ALLOWED_FILE_EXTENSIONS are considered possible Obsidian notes
ALLOWED_FILE_EXTENSIONS: List[str] = ['md', 'markdown', 'mdown', 'mkdn', 'obs']


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
    parser.add_argument('--attachments', '-a', action='store_true',
                        help='Copy attachments (from ATTACHMENT_DIRS) linked by output document set')
    parser.add_argument('--force', action='store_true',
                        help='Perform operation even if outpath is not empty (WARNING: will clobber!)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (verbose output)')
    args = parser.parse_args()

    # Set up logging
    rootlogger = logging.getLogger()
    log_format: str = "[%(filename)20s,%(lineno)3s:%(funcName)20s] %(message)s"
    logging.basicConfig(format=log_format)
    logger = logging.getLogger(__name__)
    if args.debug:
        rootlogger.setLevel(logging.DEBUG)
        logger.debug('Debug output enabled')
    else:
        rootlogger.setLevel(logging.INFO)

    vault: obs_document.ObsVault
    vault = obs_document.ObsVault(args.inpath)

    # Input sanity checks
    if os.path.isdir(args.outpath):
        if len(os.listdir(args.outpath)) != 0:
            if not args.force:
                logger.warning(f'Destination directory {args.outpath} is not empty '
                               'and --force not specified; aborting.')
                return 1

    # Convert the user-supplied string to the proper datatype
    filterfieldvalue: Any = yaml.safe_load(args.fieldvalue)
    logger.debug(f'Operation will {args.operation} '
                 f'if {args.filterfield} '
                 f'matches {filterfieldvalue} '
                 f'(type {type(filterfieldvalue)})')

    # Inspect each file and create outputlist as appropriate
    outputlist: List[obs_document.ObsDocument] = []
    for fp in vault.doclist:
        obsdoc: obs_document.ObsDocument
        obsdoc = obs_document.ObsDocument(fp)
        obsdoc.metadata = yaml.safe_load(obsdoc.frontmatter_str)

        # If operation == INCLUDE...
        if args.operation in ['INCLUDE', 'include']:
            if args.filterfield in obsdoc.metadata:
                if type(obsdoc.metadata[args.filterfield]) is list:
                    if filterfieldvalue in obsdoc.metadata[args.filterfield]:
                        outputlist.append(obsdoc)
                elif type(obsdoc.metadata[args.filterfield]) in [str, bool, float, int]:
                    if filterfieldvalue == obsdoc.metadata[args.filterfield]:
                        outputlist.append(obsdoc)
                elif type(obsdoc.metadata[args.filterfield]) is dict:
                    if filterfieldvalue == obsdoc.metadata[args.filterfield]:  # Untested!
                        outputlist.append(obsdoc)
                else:
                    raise ValueError(f'Unknown datatype in {fp.strip(os.sep).split(os.sep)[-1]}, '
                                     f'field {args.filterfield}, '
                                     f'value {obsdoc.metadata[args.filterfield]}, '
                                     f'type {type(obsdoc.metadata[args.filterfield])}')
            else:
                logger.debug(f'Field {args.filterfield} not found in doc {fp}; not including in output')
                continue

        # If operation == EXCLUDE...
        if args.operation in ['EXCLUDE', 'exclude']:
            if args.filterfield in obsdoc.metadata:
                if type(obsdoc.metadata[args.filterfield]) is list:
                    if filterfieldvalue in obsdoc.metadata[args.filterfield]:
                        continue
                    else:
                        outputlist.append(obsdoc)
                elif type(obsdoc.metadata[args.filterfield]) in [str, bool, float, int]:
                    if filterfieldvalue == obsdoc.metadata[args.filterfield]:
                        continue
                    else:
                        outputlist.append(obsdoc)
                elif type(obsdoc.metadata[args.filterfield]) is dict:
                    if filterfieldvalue == obsdoc.metadata[args.filterfield]:  # Untested!
                        continue
                else:
                    raise ValueError(f'Unknown datatype in {fp.strip(os.sep).split(os.sep)[-1]}, '
                                     f'field {args.filterfield}, '
                                     f'value {obsdoc.metadata[args.filterfield]}, '
                                     f'type {type(obsdoc.metadata[args.filterfield])}')
            else:
                logger.debug(f'Field {args.filterfield} not found in doc {fp}; appending to output')
                outputlist.append(obsdoc)
    logger.debug(f'Filtered filelist now contains {len(outputlist)} items')

    # Create a list of all internal links in all output docs
    all_links: List[str] = []
    for doc in outputlist:
        all_links.extend(doc.internal_links)

    # Cross-reference against list of all attachments and list the files that are linked
    relevant_attachments: List[str] = []
    for f in vault.allattachments:
        if any(os.path.basename(f) == s for s in all_links):
            relevant_attachments.append(f)

    #  Create a new directory hierarchy and copy/move the files on the list into it
    for doc in outputlist:
        newfp = doc.filename.replace(vault.root, args.outpath.rstrip(os.path.sep))
        pathlib.Path(os.path.dirname(newfp)).mkdir(parents=True, exist_ok=True)  # create dir tree if needed
        if args.command in ['COPY', 'copy']:
            logger.debug(f'Copying: {doc.filename} -> {newfp}')
            shutil.copy(doc.filename, newfp)
        if args.command in ['MOVE', 'move']:
            logger.debug(f'Moving: {doc.filename} -> {newfp}')
            shutil.move(doc.filename, newfp)

    # Copy the attachments in a similar way, if --attachments is selected
    if args.attachments:
        for f in relevant_attachments:
            newfp = f.replace(vault.root, args.outpath.rstrip(os.path.sep))
            pathlib.Path(os.path.dirname(newfp)).mkdir(parents=True, exist_ok=True)  # creates Attachments dirs
            logger.debug(f'Copying: {f} -> {newfp}')
            shutil.copy(f, newfp)

    return 0  # success


if __name__ == '__main__':
    sys.exit(main())
