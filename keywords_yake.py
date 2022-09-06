import sys
import argparse
import logging
import yake

import obs_document


def wikify_document(inpath, outpath):
    """Using YAKE to determine key words/phrases, 'wikify' the Obsidian
    document located at inpath, and write the resulting wiki-linked version
    to a file at outpath.

    Should be safe and not corrupt Obsidian Vault .md files, but no
    guarantees about anything else.
    """
    obsdoc = obs_document.ObsDocument()  # see obs_document.py

    obsdoc.filename = inpath
    logging.debug(f'Reading from {inpath}')
    with open(obsdoc.filename, 'r') as inf:
        obsdoc.lines = inf.readlines()
        logging.debug(f'Read {len(obsdoc.lines)} lines')

    # Number of lines per keyword... tune this based on density of content
    lines_per_kwd: int = 10
    number_of_keywords: int = int(len(obsdoc.lines[2:]) / lines_per_kwd)

    # Run the doc through YAKE and get desired number of keywords
    kws: [''] = get_keywords(obsdoc, number_of_keywords)

    # Wikify those [[terms]] throughout the document
    obsdoc.wikify_terms(kws)

    if not outpath:
        logging.debug('No output path specified, performing in-place modification')
        outpath = inpath

    logging.debug(f'Writing to {outpath}')
    with open(outpath, 'w') as outf:
        outf.writelines(obsdoc.lines)
        logging.debug(f'Wrote {len(obsdoc.lines)} lines, with {len(kws)} wikified keywords')
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
    max_ngram_size = 3
    deduplication_threshold = 0.3  # limits the duplication of words in different keywords; 0.9 is lenient (allowed)

    kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size,
                                         dedupLim=deduplication_threshold,
                                         top=numberkws, features=None)
    text: str = ''.join(content)  # TODO ignore lines that start with # (hash/pound) symbol, usually titles
    kws: [] = kw_extractor.extract_keywords(text)  # returns Union[list, list[tuple[Any, Any]]]
    logging.debug(f'Keywords are:\n{kws}')

    keywords: [''] = []
    for k in kws:
        keywords.append(k[0])  # we only care about the keyword string itself, not the numeric score
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

    # This is mostly for test purposes
    sys.exit(
        wikify_document(args.inpath, args.outpath)
    )
