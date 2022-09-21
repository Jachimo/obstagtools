# Unit tests for obs_document.py
import pytest
import oyaml as yaml
import uuid

from obs_document import ObsDocument
from obs_utilities import check_inner_type


# Negative tests

def test_exception_on_bad_docpath():
    with pytest.raises(ValueError):
        ObsDocument(None)  # type: ignore


# Positive tests
TESTDOC = 'testdata/test-structure.md'
RANDOM_TAG_NAME = str(uuid.uuid4())

@pytest.fixture
def basic_doc():
    """Returns a doc object created from TESTDOC"""
    return ObsDocument(TESTDOC)

def test_doc_validity(basic_doc):
    assert basic_doc.validate(try_redetect=False)

def test_doc_filename(basic_doc):
    assert basic_doc.filename == TESTDOC

def test_doc_lines_length(basic_doc):
    with open(basic_doc.filename, 'r') as d:
        assert len(basic_doc.lines) == len(d.readlines())

def test_doc_frontmatter_type(basic_doc):
    assert isinstance(basic_doc.frontmatter_str, str)
    assert isinstance(basic_doc.frontmatter, list)
    assert check_inner_type(basic_doc.frontmatter, str)

def test_doc_content_type(basic_doc):
    assert isinstance(basic_doc.content, list)
    assert check_inner_type(basic_doc.content, str)

def test_frontmatter_yaml_parsing(basic_doc):
    md = yaml.safe_load(basic_doc.frontmatter_str)
    assert isinstance(md, dict)
    assert check_inner_type(md.keys(), str)

def test_internal_links(basic_doc):
    assert isinstance(basic_doc.internal_links, list)
    assert check_inner_type(basic_doc.internal_links, str)

def test_add_tag(basic_doc):
    initial_md = yaml.safe_load(basic_doc.frontmatter_str)
    assert 'example' in initial_md['tags']
    assert RANDOM_TAG_NAME not in initial_md['tags']
    basic_doc.add_tag(RANDOM_TAG_NAME)
    new_md = yaml.safe_load(basic_doc.frontmatter_str)
    assert 'example' in new_md['tags']  # make sure it's not clobbered
    assert RANDOM_TAG_NAME not in new_md  # not in top-level namespace
    assert RANDOM_TAG_NAME in new_md['tags']  # should be here
