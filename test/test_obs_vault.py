# Basic unit tests for obs_vault.py
import os

import pytest

from obs_utilities import check_inner_type

from obs_vault import ObsVault
import obs_config as config


# Negative tests (fail conditions)

def test_exception_on_null_root():
    with pytest.raises(ValueError):
        ObsVault(None)  # type: ignore

def test_exception_on_int_root():
    with pytest.raises(TypeError):
        ObsVault(1)  # type: ignore

def test_exception_on_invalid_dir():
    with pytest.raises(ValueError):
        ObsVault('invalid/path/should/never/exist/')


# Positive tests (pass conditions)
TESTVAULT = config.TEST_DATA_DIR  # OOTB default is 'testdata/'

@pytest.fixture
def basic_vault():
    """Returns a vault created from testdata (in the repository)"""
    return ObsVault(TESTVAULT)

def test_vaultroot_trim(basic_vault):
    assert basic_vault.root == TESTVAULT.rstrip(os.sep)

def test_attachment_dir_length(basic_vault):
    assert len(basic_vault.attachmentdirs) == len(config.ATTACHMENT_DIRS)

def test_allattachments_null(basic_vault):
    basic_vault.attachmentdirs = None
    assert basic_vault.allattachments is None

def test_allattachments_types(basic_vault):
    assert isinstance(basic_vault.allattachments, list)
    assert check_inner_type(basic_vault.allattachments, str)

def test_doclist_types(basic_vault):
    assert isinstance(basic_vault.doclist, list)
    assert check_inner_type(basic_vault.doclist, str)

def test_doc_count(basic_vault):
    assert len(basic_vault.doclist) == len(basic_vault.docs)
