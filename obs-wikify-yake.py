import sys
import argparse
import logging
import yake

import obs_document

LINES_PER_KEYWORD: int = 5  # adjust this based on on "density" (subjective)
MAX_KEYWORD_SIZE: int = 1   # max 'n-gram' size of the 'keywords' (if >1, more accurately 'key phrases')


def main() -> int:
    parser = argparse.ArgumentParser(description='Use YAKE to make wikilinks from [[keywords]] in an Obsidian document')
    parser.add_argument('inpath', help='Input file to read from')
    parser.add_argument('outpath', nargs='?', default=False,
                        help='Output file to write to (if not provided, modify input file in-place)')
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

    if wikify_document(args.inpath, args.outpath):
        return 0
    else:
        return 1


def wikify_document(inpath: str, outpath: str) -> bool:
    """Using YAKE, extract keywords and 'wikify' an Obsidian document on disk.

    Uses YAKE for unsupervised automatic keyword extraction, and extracts
    a variable number of key words/phrases based on document length.
    All key words/phrases are then wrapped in [[brackets]] so that they are
    treated as internal wiki-type links by Obsidian and appear in the
    knowledge graph.

    Args:
        inpath: path to the input Obsidian YAML+Markdown document.
        outpath: path to write the wikified file to (if absent, modify input in-place).

    Returns:
        True if completed successfully.
    """
    logger = logging.getLogger(__name__)
    obsdoc = obs_document.ObsDocument(inpath)

    # Run the doc through YAKE and get desired number of keywords
    lines_per_kwd: int = LINES_PER_KEYWORD
    number_of_keywords: int = int(len(obsdoc.lines[2:]) / lines_per_kwd)
    kws: [''] = get_keywords(obsdoc, number_of_keywords)

    # Wikify those [[terms]]
    obsdoc.wikify_terms(kws, firstonly=True, skipheaders=True)

    if not outpath:
        logger.debug('No output path specified, performing in-place modification')
        outpath = inpath
    logger.debug(f'Writing to {outpath}')

    with open(outpath, 'w') as f:
        f.writelines(obsdoc.lines)
        logger.debug(f'Wrote {len(obsdoc.lines)} lines')

    return True


def get_keywords(obsdoc: obs_document.ObsDocument, numberkws: int) -> ['']:
    """Extract specified number of keywords from an Obsidian document.

    Uses YAKE to extract a specified number of keywords from the content
    of an Obsidian document (where the content is a list of strings).
    Returns a list of strings containing the keywords.

    Args:
        obsdoc: instance of obs_document.ObsDoc to extract keywords from
        numberkws: integer number of keywords to extract
    Returns:
        list of strings containing the keywords found
    """
    logger = logging.getLogger(__name__)

    # YAKE KeywordExtractor Configuration Parameters (play with these)
    language: str = 'en'
    max_ngram_size: int = MAX_KEYWORD_SIZE
    deduplication_threshold: float = 0.3  # limits the duplication of words in multi-word results; 0.9 is lenient

    # Retrieve Markdown content portion of the Obsidian doc, trimming off delimiter and top H1 title
    content: [''] = obsdoc.get_content()[2:]
    logger.debug(f'Content contains {len(content)} lines')

    kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size,
                                         dedupLim=deduplication_threshold,
                                         top=numberkws, features=None)

    # Filter the content to remove any lines we don't want contributing to keywords, e.g. titles/subtitles
    filteredcontent: [''] = []
    for line in content:
        if not line.strip():  # for whitespace-only lines
            continue
        if line.strip()[0] == '#':  # for titles
            continue
        else:
            filteredcontent.append(line)
    text: str = ''.join(filteredcontent)

    kws: [] = kw_extractor.extract_keywords(text)  # returns [(str, float)]
    logger.debug(f'YAKE returned:\n{kws}')

    keywords: [''] = []
    for k in kws:
        keywords.append(k[0])  # we only care about the keyword string itself, not the numeric score
    return keywords


if __name__ == '__main__':
    sys.exit(main())
