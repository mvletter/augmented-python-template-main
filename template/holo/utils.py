from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, TypeVar
from uuid import UUID


T = TypeVar("T")


class SingletonMeta[T](type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose. Would become obsolete
    when we have a proper depedancy injection solution.
    """

    _instances: dict[SingletonMeta[T], T] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> T:
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


def to_json_string(obj):
    """
    Helper util for serializing certain types of objects to JSON.

    Params:
        obj (object): Object being serialized into json.

    Returns:
        str: Representation of the object being serialized.

    Raises:
        TypeError: If an unknown object type is being serialized.
    """
    if isinstance(obj, date | datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal | UUID):
        return str(obj)
    else:
        raise TypeError(f"Unable to serialize type {type(obj)}.")
