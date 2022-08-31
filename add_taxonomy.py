#!/usr/bin/env python3
import argparse
import logging
import sys
from typing import TextIO

import oyaml as yaml

import obs_document


def main() -> int:  # returns Unix exit value
    parser = argparse.ArgumentParser(description='Reformat Obsidian frontmatter to conform to a specified taxonomy')
    parser.add_argument('inpath', help='Input file to add tags to')
    parser.add_argument('outpath', nargs='?', default=False,
                        help='Output file to write to (in-place modification if not given)')
    parser.add_argument('--taxonomy', '-T', default=False, help='YAML taxonomy file (default: metadata.yaml)')
    parser.add_argument('--no-clean', help='Keep existing metadata fields not present in taxonomy',
                        action='store_true')
    parser.add_argument('--debug', help='Enable debug mode (verbose output)', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug output enabled')
    else:
        logging.basicConfig(level=logging.INFO)

    if not args.taxonomy:
        logging.debug('No taxonomy specified, defaulting to metadata.yaml')
        args.taxonomy = 'metadata.yaml'

    if not args.outpath:
        logging.debug('No output path specified, performing in-place modification')
        args.outpath = args.inpath

    obsdoc = obs_document.ObsDocument()  # see obs_document.py
    obsdoc.filename = args.inpath

    logging.debug(f'Reading from {args.inpath}')

    with open(args.inpath, 'r') as infile:
        obsdoc.lines = infile.readlines()
        logging.debug(f'Read {len(obsdoc.lines)} lines')

    # Retrieve YAML frontmatter portion of the Obsidian doc
    metadata: dict = yaml.safe_load(obsdoc.get_frontmatter())
    logging.debug(f'Frontmatter YAML parsed as:\n{metadata}\n')
    yaml.dump(metadata, sys.stdout)  # remove after debugging

    with open(args.taxonomy, 'r') as taxofile:
        # Read JSON (or YAML? or simpler?) taxonomy file specifying metadata fields, types, and default values
        pass

    # Construct new frontmatter using taxonomy as definition
    #   - If field is in taxonomy AND in document already, keep and use document value
    #   - If field is in taxonomy BUT NOT in document already, add it and use default value
    #   - IF NO-CLEAN SELECTED: If field is *not* in taxonomy BUT IS in document, keep and use doc value

    # Regenerate YAML frontmatter and combine with content to make new document text

    # Write out frontmatter+content (YAML+Markdown) to desired output path
    return 0


if __name__ == '__main__':
    sys.exit(main())
