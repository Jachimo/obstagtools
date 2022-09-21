# Utility functions
# Part of 'Obsidian Tag Tools': https://github.com/Jachimo/obstagtools

from typing import Iterable, Type


def check_inner_type(iterable: Iterable, tp: Type) -> bool:
    """Check inner types of a nested object, e.g. list of strings

    Args:
        iterable: iterable 'outer' object
        tp: desired type of each 'inner' object

    Returns:
        True if all 'inner' objects are of type tp
        False if any are not
    """
    return all(isinstance(i, tp) for i in iterable)
