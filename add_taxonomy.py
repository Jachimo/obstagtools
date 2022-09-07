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

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug output enabled')
    else:
        logging.basicConfig(level=logging.INFO)

    if not args.outpath:
        logging.debug('No output path specified, performing in-place modification')
        args.outpath = args.inpath

    obsdoc = obs_document.ObsDocument(args.inpath)  # see obs_document.py

    # Retrieve YAML frontmatter portion of the Obsidian doc
    metadata: dict = yaml.safe_load(obsdoc.get_frontmatter_str())
    logging.debug(f'Frontmatter YAML parsed as:\n{metadata}')

    # Read YAML taxonomy file specifying metadata fields and default values
    logging.debug(f'Attempting to read taxonomy from {args.taxonomy}')
    with open(args.taxonomy, 'r') as tf:
        taxo: dict = yaml.safe_load(tf)
        logging.debug(f'Taxonomy YAML parsed as:\n{taxo}')

    newfm: dict = {}  # new frontmatter
    keylist: list

    if args.clean:  # if --clean is selected
        keylist = list(taxo.keys())  # iterate over *only* keys in the taxonomy (effectively removes all others)
    else:  # but normally, when --clean is *not* selected
        keylist = list(taxo.keys())
        keylist.extend(x for x in list(metadata.keys()) if x not in keylist)  # https://stackoverflow.com/a/43325018/

    for k in keylist:  # see above how keylist depends on --clean option
        if k in metadata:
            if (type(metadata[k]) is list) or (type(taxo[k]) is list):  # if the doc *or* taxo value is a list
                if type(metadata[k]) is str:
                    metadata[k] = [metadata[k]]  # make sure that they are *both* lists so we can combine
                if type(taxo[k]) is str:
                    taxo[k] = [taxo[k]]
                newfm[k] = list(set(taxo[k] + metadata[k]))  # combine the lists, remove duplicates with list(set([]))
            else:
                newfm[k] = metadata[k]  # for single-valued fields, prefer value on document
        else:
            newfm[k] = taxo[k]  # if field not on doc already, use default value from taxonomy file

    logging.debug(f'Keeping {len(newfm)} fields, from {len(metadata.keys())} document '
                  f'and {len(taxo.keys())} taxonomy fields '
                  f'({len([key for key in taxo.keys() or metadata.keys()])} total unique)')
    logging.debug('New metadata:\n' + str(newfm))

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
        logging.debug('Skipping indentation due to --noindent option')

    # Replace existing frontmatter in the ObsDocument
    obsdoc.set_frontmatter(newfmlines)

    # Write out frontmatter+content (YAML+Markdown) to desired output path
    with open(args.outpath, 'w') as outf:
        outf.writelines(obsdoc.lines)
    return 0


if __name__ == '__main__':
    sys.exit(main())
