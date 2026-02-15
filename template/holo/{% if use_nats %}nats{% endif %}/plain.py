import logging
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from holo.adapters.nats.events import BaseEvent
from holo.nats.client import HoloNats, NatsSubscription


T = TypeVar("T")
P = ParamSpec("P")


logger = logging.getLogger(__name__)


class NatsSubscriber:
    def __init__(self) -> None:
        self.subscriptions: list[NatsSubscription] = []
        self.connection: HoloNats

    def subscribe(
        self,
        subject: str,
        models: type[BaseEvent] | tuple[type[BaseEvent], ...],
        max_tasks: int = 1,
        queue: str = "",
        ignore: type[BaseEvent] | tuple[type[BaseEvent], ...] | None = None,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        def add_subscription(func: Callable[P, T]) -> Callable[P, T]:
            self.subscriptions.append(NatsSubscription(subject, models, func, max_tasks, queue, ignore=ignore))
            return func

        return add_subscription

    async def publish(self, subject: str, payload: bytes = b"") -> None:
        await self.connection.publish(subject=subject, payload=payload)

    async def connect(self, con: HoloNats, consumer_name: str) -> None:
        self.connection = con
        self.consumer_name = consumer_name

    async def start(self) -> None:
        for subscription in self.subscriptions:
            queue = subscription.queue or f"{self.consumer_name}-{subscription.subject}"
            logger.info("Adding NATS listener for %s", subscription.subject)
            logger.info("Using queue: %s", queue)
            await self.connection.subscribe(
                subject=subscription.subject,
                cb=subscription.on_message,
                queue=queue,
                max_tasks=subscription.max_tasks,
            )

    async def disconnect(self) -> None:
        # Nothing to disconnect.
        pass
