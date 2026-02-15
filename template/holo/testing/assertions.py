import unittest
from collections.abc import Iterable

from pydantic import ValidationError


def field_in_validation_error(field_name: str, validation_error: ValidationError) -> bool:
    """
    Check if a field name is present in a validation error.
    """
    return any(field_name in error["loc"] for error in validation_error.errors())


def count_equal(list_1: Iterable, list_2: Iterable) -> bool:
    """
    Check if two lists have the same elements, the same number of times,
    without regard to order.
    """
    # Check for both arguments that they are not of type dict, because using
    # dicts with assertCountEqual will only check the keys for equality.
    if isinstance(list_1, dict) or isinstance(list_2, dict):
        raise TypeError("Do not use dicts with this function")

    case = unittest.TestCase()
    case.assertCountEqual(list_1, list_2)  # Raises AssertionError if not equal
    return True


list_items_equal = count_equal
