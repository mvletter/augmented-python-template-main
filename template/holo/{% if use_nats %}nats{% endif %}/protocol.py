from typing import Protocol

from holo.nats.client import HoloNats


class NatsSubscriberProtocol(Protocol):
    async def start(self) -> None: ...

    async def disconnect(self) -> None: ...

    async def connect(self, con: HoloNats, consumer_name: str) -> None: ...
