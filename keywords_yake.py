import sys
import argparse
import logging
import oyaml as yaml
import yake

import obs_document


def main(arguments):
    obsdoc = obs_document.ObsDocument()  # see obs_document.py
    obsdoc.filename = arguments.inpath
    logging.debug(f'Reading from {arguments.inpath}')

    with open(obsdoc.filename, 'r') as inf:
        obsdoc.lines = inf.readlines()
        logging.debug(f'Read {len(obsdoc.lines)} lines')

    # Retrieve YAML frontmatter portion of the Obsidian doc
    #metadata: dict = yaml.safe_load(obsdoc.get_frontmatter())
    #logging.debug(f'Frontmatter YAML parsed as:\n{metadata}')

    # Number of lines per keyword... tune this based on density of content
    lines_per_kwd: int = 5
    number_of_keywords: int = int(len(obsdoc.lines[2:]) / lines_per_kwd)

    # Run the doc through YAKE and get desired number of keywords
    kws: [''] = get_keywords(obsdoc, number_of_keywords)

    # Wikify [[those]] terms throughout the document
    obsdoc.wikify_terms(kws)

    if not arguments.outpath:
        logging.debug('No output path specified, performing in-place modification')
        arguments.outpath = arguments.inpath

    logging.debug(f'Writing to {arguments.outpath}')
    with open(arguments.outpath, 'w') as outf:
        outf.writelines(obsdoc.lines)
    return 0


def get_keywords(obsdoc, numberkws: int) -> ['']:
    """Use YAKE to extract a specified number of keywords from a
    list of strings representing lines of text content. Return a
    list of strings containing the keywords."""

    # Retrieve Markdown content portion of the Obsidian doc, trimming off delimiter and top H1 title
    content: [''] = obsdoc.get_content()[2:]
    logging.debug(f'Content contains {len(content)} lines')

    # YAKE KeywordExtractor Configuration Parameters (play with these)
    language = 'en'
    max_ngram_size = 2
    deduplication_threshold = 0.9  # limits the duplication of words in different keywords; 0.9 is lenient (allowed)

    kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size,
                                         dedupLim=deduplication_threshold,
                                         top=numberkws, features=None)
    text = ''.join(content)
    kws = kw_extractor.extract_keywords(text)
    logging.debug(f'Keywords are:\n{kws}')

    keywords: [''] = []
    for k in kws:
        keywords.append(k[0])
    return keywords


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Use YAKE to extract keywords from Obsidian document content')
    parser.add_argument('inpath', help='Input file to read from')
    parser.add_argument('outpath', nargs='?', default=False,
                        help='Output file to write to (if not provided, modify input file in-place)')
    parser.add_argument('--debug', help='Enable debug mode (verbose output)', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug output enabled')
    else:
        logging.basicConfig(level=logging.INFO)

    sys.exit(main(args))
