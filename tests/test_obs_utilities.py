# Unit tests for obs_utilities.py
import pytest

from obs_utilities import check_inner_type

LIST_OF_STRINGS = ['one', 'two', 'three']
BAD_LOS = LIST_OF_STRINGS + [4]
LIST_OF_INTS = [1, 2, 3]
BAD_LOI = LIST_OF_INTS + ['four']
DICT_STRING_KEYS = {'species': 'cat', 'name': 'felix'}

def test_cit_list_positive():
    assert check_inner_type(LIST_OF_STRINGS, str)
    assert check_inner_type(LIST_OF_INTS, int)

def test_cit_list_negative():
    assert not check_inner_type(BAD_LOS, str)
    assert not check_inner_type(BAD_LOI, int)

def test_cit_dict():
    assert check_inner_type(DICT_STRING_KEYS.keys(), str)
