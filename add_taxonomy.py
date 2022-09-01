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
    parser.add_argument('--clean', help='Remove all input document fields not present in taxonomy',
                        default=False, action='store_true')
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

    with open(args.inpath, 'r') as inf:
        obsdoc.lines = inf.readlines()
        logging.debug(f'Read {len(obsdoc.lines)} lines')

    # Retrieve YAML frontmatter portion of the Obsidian doc
    metadata: dict = yaml.safe_load(obsdoc.get_frontmatter())
    logging.debug(f'Frontmatter YAML parsed as:\n{metadata}')
    #yaml.dump(metadata, sys.stdout)  # remove after debugging

    with open(args.taxonomy, 'r') as tf:
        # Read YAML taxonomy file specifying metadata fields and default values
        taxo: dict = yaml.safe_load(tf)
        logging.debug(f'Taxonomy YAML parsed as:\n{taxo}')

    # Construct new frontmatter using taxonomy as definition
    #   - If field is in taxonomy AND in document already, keep and use document value
    #   - If field is in taxonomy BUT NOT in document already, add it and use default (taxonomy-provided) value
    #   - IF NOT --clean: If field is in document BUT NOT in taxonomy, keep and use document value
    #   - IF --clean: If field is in document BUT NOT in taxonomy, remove it

    newfm: dict = {}  # new frontmatter
    keylist: list

    if args.clean:  # if --clean is selected
        keylist = list(taxo.keys())  # iterate over *only* keys in the taxonomy (effectively removes all others)
    else:  # but normally, when --clean is *not* selected
        keylist = list(set(taxo.keys()).union(set(metadata.keys())))  # iterate over all keys in *both* lists

    for k in keylist:  # see above how keylist depends on --clean option
        if k in metadata:
            if (type(metadata[k]) is list) or (type(taxo[k]) is list):  # if the doc *or* taxo value is a list
                if type(metadata[k]) is str:
                    metadata[k] = [metadata[k]]  # if either is a string, convert into 1-item list
                if type(taxo[k]) is str:
                    taxo[k] = [taxo[k]]
                newfm[k] = taxo[k] + metadata[k]  # combine the lists
                # TODO: need to deduplicate newfm - if same tag is in both doc and taxo default, shouldn't appear 2x
            else:
                newfm[k] = metadata[k]  # for single-valued fields, prefer value on document
        else:
            newfm[k] = taxo[k]  # use default value from taxonomy file

    logging.debug(f'Keeping {len(newfm)} fields, from {len(metadata.keys())} document '
                  f'and {len(taxo.keys())} taxonomy fields '
                  f'({len([key for key in taxo.keys() or metadata.keys()])} total unique)')
    logging.debug('New metadata:\n' + str(newfm))

    # Regenerate YAML frontmatter and combine with content to make new document text
    newfmlines: [''] = (yaml.dump(newfm, default_flow_style=False)).splitlines(keepends=True)
    obsdoc.replace_frontmatter(newfmlines)

    # Write out frontmatter+content (YAML+Markdown) to desired output path
    with open(args.outpath, 'w') as outf:
        outf.writelines(obsdoc.lines)

    return 0


if __name__ == '__main__':
    sys.exit(main())
