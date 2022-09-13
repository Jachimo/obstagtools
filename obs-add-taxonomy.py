#!/usr/bin/env python3
import argparse
import logging
import sys
import oyaml as yaml

import obs_document


def main() -> int:  # returns Unix exit value
    parser = argparse.ArgumentParser(description='Reformat Obsidian frontmatter to conform to a specified taxonomy')
    parser.add_argument('inpath', help='Input file to read from')
    parser.add_argument('outpath', nargs='?', default=False,
                        help='Output file to write to (if not provided, modify input file in-place)')
    parser.add_argument('--taxonomy', '-T', default='metadata.yaml', help='YAML taxonomy file (default: metadata.yaml)')
    parser.add_argument('--clean', help='Remove all input document fields not present in taxonomy (DESTRUCTIVE!)',
                        default=False, action='store_true')
    parser.add_argument('--noindent', help='Do not indent YAML sequences (may break other tools)',
                        default=False, action='store_true')
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

    if not args.outpath:
        logger.debug('No output path specified, performing in-place modification')
        args.outpath = args.inpath

    obsdoc = obs_document.ObsDocument(args.inpath)  # see obs_document.py

    # Retrieve YAML frontmatter portion of the Obsidian doc
    metadata: dict = yaml.safe_load(obsdoc.frontmatter_str)
    logger.debug(f'Frontmatter YAML parsed as:\n{metadata}')

    # Read YAML taxonomy file specifying metadata fields and default values
    logger.debug(f'Attempting to read taxonomy from {args.taxonomy}')
    with open(args.taxonomy, 'r') as tf:
        taxo: dict = yaml.safe_load(tf)
        logger.debug(f'Taxonomy YAML parsed as:\n{taxo}')

    newfm: dict = {}  # new frontmatter
    keylist: list

    if args.clean:  # if --clean is selected
        keylist = list(taxo.keys())  # iterate over *only* keys in the taxonomy (effectively removes all others)
    else:  # but normally, when --clean is *not* selected
        keylist = list(taxo.keys())
        keylist.extend(x for x in list(metadata.keys()) if x not in keylist)  # https://stackoverflow.com/a/43325018/

    for k in keylist:  # see above how keylist depends on --clean option
        logger.debug(f'Processing field "{k}"')
        if k in metadata:  # if field exists on the document...
            logger.debug(f'Field "{k}" exists on document, type {type(metadata[k])}')
            if k in taxo:  # AND on the taxonomy...
                logger.debug(f'Field "{k}" also exists on taxonomy, type {type(taxo[k])}')
                if (type(metadata[k]) is list) or (type(taxo[k]) is list):  # if either value is a list
                    if type(metadata[k]) is str:
                        metadata[k] = [metadata[k]]  # make sure that they are *both* lists...
                    if type(taxo[k]) is str:
                        taxo[k] = [taxo[k]]
                    newfm[k] = taxo[k]
                    newfm[k].extend(x for x in metadata[k] if x not in newfm[k])  # ...and combine, preserving order
                    logger.debug(f'Combined doc list {metadata[k]} with taxo list {taxo[k]}, yielding {newfm[k]}')
                else:  # for anything else other than a list...
                    logger.debug(f'Preserving doc value "{metadata[k]}"')
                    newfm[k] = metadata[k]  # ...just use the value on the document, overriding taxonomy default
            else:
                logger.debug(f'Field "{k}" found on doc but not in taxo, preserving doc value "{metadata[k]}"')
                newfm[k] = metadata[k]
        else:  # but if field is NOT on doc already...
            logger.debug(f'Field "{k}" not found on doc, using default value "{taxo[k]}"')
            newfm[k] = taxo[k]  # ...just use default value from taxonomy file

    logger.debug(f'Keeping {len(newfm)} fields, from {len(metadata.keys())} document '
                  f'and {len(taxo.keys())} taxonomy fields '
                  f'({len([key for key in taxo.keys() or metadata.keys()])} total unique)')
    logger.debug('New metadata:\n' + str(newfm))

    # Serialize YAML frontmatter into lines
    newfmlines: [''] = (yaml.dump(newfm, explicit_start=True, default_flow_style=False)).splitlines(keepends=True)

    # By default, indent YAML sequences unless --noindent is specified
    if not args.noindent:  # args.noindent defaults to False, so this is default behavior
        for i in range(0, len(newfmlines)):
            if (newfmlines[i][:2] == '- ') and (newfmlines[i-1][-2:] == ':\n'):
                newfmlines[i] = '  ' + newfmlines[i]  # indent first YAML sequence item inside a mapping
            if (newfmlines[i][:2] == '- ') and (newfmlines[i-1][:4] == '  - '):
                newfmlines[i] = '  ' + newfmlines[i]  # indent subsequent sequence items
    else:
        logger.debug('Skipping indentation due to --noindent option')

    # Replace existing frontmatter in the ObsDocument
    obsdoc.frontmatter = newfmlines

    # Write out frontmatter+content (YAML+Markdown) to desired output path
    with open(args.outpath, 'w') as outf:
        outf.writelines(obsdoc.lines)
    return 0


if __name__ == '__main__':
    sys.exit(main())
