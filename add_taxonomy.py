#!/usr/bin/env python3
import argparse
import logging
import sys

import obs_document


def main() -> int:  # returns Unix exit value
    parser = argparse.ArgumentParser(description='Reformat Obsidian frontmatter to conform to a specified taxonomy')
    parser.add_argument('inpath', help='Input file to add tags to')
    parser.add_argument('outpath', nargs='?', default=False,
                        help='Output file to write to (in-place modification if not given)')
    parser.add_argument('--taxonomy', '-T', default=False, help='JSON taxonomy file to use')
    # TODO: add '--no-clean' to preserve additional fields on doc that are not in taxonomy (remove extras by default)
    parser.add_argument('--debug', help='Enable debug mode (verbose output)', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug output enabled')
    else:
        logging.basicConfig(level=logging.INFO)

    if not args.taxonomy:
        logging.info('No taxonomy specified, exiting')
        return 1

    if not args.outpath:
        logging.debug('No output path specified, performing in-place modification')
        args.outpath = args.inpath

    obsdoc = obs_document.ObsDocument()  # see obs_document.py

    logging.debug(f'Reading from {args.inpath}')
    with open(args.inpath, 'r') as infile:
        obsdoc.filename = args.inpath
        obsdoc.lines = infile.readlines()
        logging.debug(f'Read {len(obsdoc.lines)} lines')

    with open(args.taxonomy, 'r') as taxfile:
        # Read JSON (or YAML? or simpler?) taxonomy file specifying metadata fields, types, and default values

    # Remove/save document content (after frontmatter end) to separate attribute
    # Read and parse the YAML frontmatter of the Obsidian doc
    # Construct new frontmatter using taxonomy as definition
    #   - If field is in taxonomy AND in document already, keep and use document value
    #   - If field is in taxonomy BUT NOT in document already, add it and use default value
    #   - IF NO-CLEAN SELECTED: If field is *not* in taxonomy BUT IS in document, keep and use doc value

    # Regenerate YAML frontmatter and combine with content to make new document text

    # Write out frontmatter+content (YAML+Markdown) to desired output path

if __name__ == '__main__':
    sys.exit(main())
