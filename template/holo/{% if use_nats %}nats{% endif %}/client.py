import asyncio
import logging
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from time import perf_counter
from typing import Annotated, Any, Union

from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.aio.subscription import Subscription
from nats.js.api import ConsumerConfig
from pydantic import Field, TypeAdapter, ValidationError

from holo.adapters.nats.events import BaseEvent
from holo.nats.exceptions import NakException
from holo.nats.metrics import EVENT_NAKS, EVENTS_WAITING, EVENTS_WAITING_TIME, EVENTS_WAITING_TIMEOUTS, EXCEPTIONS


logger = logging.getLogger(__name__)


class HoloNatsConcurrentSubscribeMixin:
    # This set is used to gather async background tasks, to prevent them being garbage collected mid execution.
    # See: https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
    background_tasks = set()

    background_task_info: dict[str, dict[str, Any]]

    def __init__(self, *args, **kwargs) -> None:
        self.background_task_info = {}
        super().__init__(*args, **kwargs)

    async def subscribe(
        self,
        subject: str,
        *args,
        max_tasks: int | None = None,
        ack_wait=30,
        **kwargs,
    ) -> Subscription:
        """
        Create subscriber with concurrency support when needed.
        """
        if max_tasks:
            self.background_task_info[subject] = {
                "max": max_tasks,
                "active": 0,
                "lock": asyncio.Lock(),
            }

            original_callback = kwargs["cb"]

            # The `subject` argument is the full topic, eg. "SIP.account.changed.v1".
            subject_parts = subject.rsplit(".", 2)
            labels = {
                "subject": subject_parts[0],
                "eventtype": subject_parts[1],
                "version": subject_parts[2],
            }
            EVENTS_WAITING.labels(**labels)
            EVENTS_WAITING_TIMEOUTS.labels(**labels)
            EVENTS_WAITING_TIME.labels(**labels)

            async def callback_release_lock(msg):
                EVENTS_WAITING.labels(**labels).dec()
                try:
                    await original_callback(msg)
                finally:
                    async with self.background_task_info[msg.subject]["lock"]:
                        self.background_task_info[msg.subject]["active"] -= 1

            async def callback_acquire_lock(msg):
                EVENTS_WAITING.labels(**labels).inc()
                try:
                    async with asyncio.timeout(ack_wait):
                        before_time = perf_counter()
                        while True:
                            async with self.background_task_info[msg.subject]["lock"]:
                                if (
                                    self.background_task_info[msg.subject]["active"]
                                    < self.background_task_info[msg.subject]["max"]
                                ):
                                    self.background_task_info[msg.subject]["active"] += 1
                                    after_time = perf_counter()
                                    EVENTS_WAITING_TIME.labels(**labels).observe(after_time - before_time)
                                    break
                                else:
                                    await asyncio.sleep(0.001)
                except TimeoutError:
                    EVENTS_WAITING_TIMEOUTS.labels(**labels).inc()
                    EVENTS_WAITING.labels(**labels).dec()
                else:
                    task = asyncio.create_task(callback_release_lock(msg))

                    # Add task to the set. This crates a strong reference.
                    self.background_tasks.add(task)
                    # To prevent keeping references to finished tasks forever,
                    # make each task remove its own reference from the set after
                    # completion:
                    task.add_done_callback(self.background_tasks.discard)

            kwargs["cb"] = callback_acquire_lock

        return await super().subscribe(subject, *args, **kwargs)


class HoloNats(HoloNatsConcurrentSubscribeMixin, Client):
    """
    Asyncio based client for NATS with support for concurrent handlers.
    """


class NatsSubscription:
    def __init__(
        self,
        subject: str,
        models: type[BaseEvent] | tuple[type[BaseEvent], ...],
        handler: Callable,
        max_tasks: int,
        queue: str | None = None,
        ack_msg: bool = False,
        config: ConsumerConfig | None = None,
        ignore: type[BaseEvent] | tuple[type[BaseEvent], ...] | None = None,
    ) -> None:
        self.subject = subject
        self.handler = handler
        self.max_tasks = max_tasks
        self.queue = queue
        self.ack_msg = ack_msg
        self.config = config
        self.ignored_models = ignore

        if isinstance(models, Iterable):
            self.models = models
        else:
            self.models = (models,)

    async def on_message(self, msg: Msg) -> None:
        try:
            Model = Annotated[Union[*self.models], Field(discriminator="name")]
            model = TypeAdapter(Model).validate_json(msg.data.decode())

            # Check if the model is a container consisting of multiple schemas. If so, the schema that the model is
            # valid for will be located in __root__. Use that specific schema instead of the container schema.
            if hasattr(model, "__root__"):
                model = model.__root__  # type: ignore
        except ValidationError as error:
            if self.ack_msg:
                await msg.ack()  # ack to avoid retrying messages we cannot handle
            logger.exception("Couldn't validate message: %s. Errors: %s", msg, error.errors())
        else:
            if self.ignored_models and isinstance(model, self.ignored_models):
                logger.debug("Ignored event %s", model.__class__.__name__)
                await msg.ack()
            else:
                try:
                    await self.handler(model)
                except NakException as e:
                    subject, eventtype, version = msg.subject.rsplit(".", 2)

                    utcnow = datetime.now(UTC)
                    if utcnow - model.time > e.max_delay:
                        EXCEPTIONS.labels(subject=subject, eventtype=eventtype, version=version).inc()

                        if hasattr(e, "__cause__") and e.__cause__:
                            raise e.__cause__
                        else:
                            raise

                    EVENT_NAKS.labels(subject=subject, eventtype=eventtype, version=version).inc()
                    await msg.nak(delay=e.delay)
                else:
                    if self.ack_msg:
                        await msg.ack()  # ack after successful handle
