from typing import TypeVar

from polyfactory.factories.pydantic_factory import ModelFactory

from holo.adapters.nats.events import BaseEvent


T = TypeVar("T")


class BaseEventFactory[T: BaseEvent](ModelFactory[T]):
    __is_base_factory__ = True
