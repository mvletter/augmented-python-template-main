from typing import Literal

from holo.adapters.nats.events import BaseEvent


class FlushDbEvent(BaseEvent):
    name: Literal["flush_db"]
