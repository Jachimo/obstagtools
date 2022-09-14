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
import re
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
    logger = logging.getLogger(__name__)
    log_format: str = "[%(filename)20s,%(lineno)3s:%(funcName)20s] %(message)s"
    logging.basicConfig(format=log_format)
    if args.debug:
        rootlogger.setLevel(logging.DEBUG)
        logger.debug('Debug output enabled')
    else:
        rootlogger.setLevel(logging.INFO)

    # Input sanity checks
    if not os.path.isdir(args.inpath):
        logger.info('Input path must refer to a directory.')
        return 1
    if os.path.isdir(args.outpath):
        if len(os.listdir(args.outpath)) != 0:
            if not args.force:
                logger.warning(f'Destination directory {args.outpath} is not empty '
                               'and --force not specified; aborting.')
                return 1

    # Build list of files to filter, based on extension
    filelist: List[str] = []
    for root, dirs, files in os.walk(args.inpath):
        for f in files:
            if any(s in root for s in SKIP_DIRS):  # don't add files from SKIP_DIRS
                continue
            elif any(s in root for s in ATTACHMENT_DIRS):  # or ATTACHMENT_DIRS
                continue
            elif f.split('.')[-1] in ALLOWED_FILE_EXTENSIONS:
                filelist.append(f'{root}{os.sep}{f}')
    logger.debug(f'Unfiltered filelist contains {len(filelist)}')

    # Convert the user-supplied string to the proper datatype
    filterfieldvalue: Any = yaml.safe_load(args.fieldvalue)
    logger.debug(f'Operation will {args.operation} '
                 f'if {args.filterfield} '
                 f'matches {filterfieldvalue} '
                 f'(type {type(filterfieldvalue)})')

    # Inspect each file and create outputlist as appropriate
    outputlist: List[obs_document.ObsDocument] = []
    for fp in filelist:
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
                    if filterfieldvalue == obsdoc.metadata[args.filterfield]:  # May want to consider special handling here?
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
                    if filterfieldvalue == obsdoc.metadata[args.filterfield]:  # May want to consider special handling here
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
    #  Note that this regex isn't perfect and is subject to false-positives, esp. w/ metacommentary about syntax
    link_regexp_expr: str = r"\[\[(.{4,}?)(?:\||\]\])"  # See https://regex101.com/r/kEmr3g/2
    link_regexp: re.Pattern = re.compile(link_regexp_expr, re.MULTILINE)
    attachmentfileslist: List[str] = []
    for doc in outputlist:
        doclinks: List[str] = re.findall(link_regexp, ''.join(doc.lines))
        for link in doclinks:
            attachmentfileslist.append(link)

    # Cross-reference against list of all attachments and list the files that are linked
    relevantattachmentslist: List[str] = []
    for d in ATTACHMENT_DIRS:
        for root, dirs, files in os.walk(f'{args.inpath.strip(os.sep)}{os.sep}{d}'):
            for f in files:
                if any(f == s for s in attachmentfileslist):
                    relevantattachmentslist.append(f'{root}{os.sep}{f}')

    #  Create a new directory hierarchy and copy/move the files on the list into it
    for doc in outputlist:
        newfp = f'{args.outpath.strip(os.sep)}{os.sep}{doc.filename.strip(os.sep).split(os.sep, 1)[-1]}'
        pathlib.Path(os.path.dirname(newfp)).mkdir(parents=True, exist_ok=True)  # create dir tree if needed
        if args.command in ['COPY', 'copy']:
            logger.debug(f'Copying: {doc.filename} -> {newfp}')
            shutil.copy(doc.filename, newfp)
        if args.command in ['MOVE', 'move']:
            logger.debug(f'Moving: {doc.filename} -> {newfp}')
            shutil.move(doc.filename, newfp)

    # Copy the attachments in a similar way, if --attachments is selected
    if args.attachments:
        for f in relevantattachmentslist:
            newfp = f'{args.outpath.strip(os.sep)}{os.sep}{f.strip(os.sep).split(os.sep, 1)[-1]}'
            pathlib.Path(os.path.dirname(newfp)).mkdir(parents=True, exist_ok=True)  # creates Attachments dirs
            logger.debug(f'Copying: {f} -> {newfp}')
            shutil.copy(f, newfp)

    return 0  # success


if __name__ == '__main__':
    sys.exit(main())
