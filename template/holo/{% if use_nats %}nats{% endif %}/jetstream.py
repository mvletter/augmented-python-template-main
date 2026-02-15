import asyncio
import contextlib
import logging
import re
from collections import deque
from collections.abc import Callable, Coroutine
from time import perf_counter
from typing import Any

from nats.errors import ConnectionClosedError
from nats.js import JetStreamContext
from nats.js.api import ConsumerConfig, PubAck, StreamConfig
from nats.js.errors import NotFoundError

from holo.adapters.nats.events import BaseEvent
from holo.config import config
from holo.nats.client import HoloNats, NatsSubscription
from holo.nats.metrics import EVENTS_WAITING, EVENTS_WAITING_TIME, EVENTS_WAITING_TIMEOUTS


logger = logging.getLogger(__name__)


class NatsStreamSubscriber:
    def __init__(self, name: str) -> None:
        self.stream_name: str = name
        self.js: JetStreamContext

        self.subscribers: list[NatsPullSubscriber] = []

    def subscribe(
        self,
        subject: str,
        models: type[BaseEvent] | tuple[type[BaseEvent], ...],
        max_tasks: int = 1,
        queue: str | None = None,
        ack_msg: bool = True,
        config: ConsumerConfig | None = None,
        ignore: type[BaseEvent] | tuple[type[BaseEvent], ...] | None = None,
    ) -> Callable:
        def add_subscription(func):
            subscription = NatsSubscription(
                subject,
                models,
                func,
                max_tasks,
                queue,
                ack_msg=ack_msg,
                config=config,
                ignore=ignore,
            )
            self.subscribers.append(NatsPullSubscriber(subscription))
            return func

        return add_subscription

    async def publish(self, subject: str, payload: bytes = b"") -> PubAck:
        return await self.js.publish(subject=f"{self.stream_name}.{subject}", payload=payload)

    async def connect(self, con: HoloNats, consumer_name: str) -> None:
        js_opts = {}
        if config.service.ENVIRONMENT and not config.service.TESTING:
            js_opts["domain"] = "voipgrid"
        self.js = con.jetstream(**js_opts)

        # Create the stream if it doesn't exist yet.
        try:
            await self.js.stream_info(self.stream_name)
        except NotFoundError:
            await self.js.add_stream(
                name=self.stream_name,
                subjects=[f"{self.stream_name}.>"],
                config=StreamConfig(num_replicas=3),
            )

        for subscriber in self.subscribers:
            await subscriber.connect(
                self.stream_name,
                consumer_name,
                self.js,
            )

    async def start(self) -> None:
        for subscriber in self.subscribers:
            await subscriber.start()

    async def disconnect(self) -> None:
        tasks = set()
        for subscriber in self.subscribers:
            tasks.add(asyncio.create_task(subscriber.disconnect()))

        with contextlib.suppress(TimeoutError, asyncio.CancelledError):
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=1)


class NatsPullSubscriber:
    # This set is used to gather async background tasks, to prevent them being garbage collected mid execution.
    # See: https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
    tasks: set[asyncio.Task]

    subscription: NatsSubscription
    running: bool = False

    max_tasks: int
    active_tasks: int

    message_queue: asyncio.Queue
    pull_event: asyncio.Event

    task_lock: asyncio.Lock
    notify_lock: asyncio.Condition

    def __init__(self, subscription: NatsSubscription) -> None:
        self.subscription = subscription

    async def connect(
        self,
        stream_name: str,
        consumer_name: str,
        stream: JetStreamContext,
    ) -> None:
        self.tasks = set()

        self.running = False

        self.max_tasks = self.subscription.max_tasks
        self.active_tasks = 0

        self.message_queue = asyncio.Queue()
        self.pull_event = asyncio.Event()

        self.task_lock = asyncio.Lock()
        self.notify_lock = asyncio.Condition(self.task_lock)

        self.stream_name = stream_name
        self.consumer_name = consumer_name
        self.js = stream

        name = re.sub("[*>]", "", self.subscription.subject.replace(".", "-"))
        queue = self.subscription.queue or f"{self.consumer_name}-{self.stream_name}-{name}"

        # The `subject` argument is the full topic, eg. "SIP.account.changed.v1".
        self.subject = f"{self.stream_name}.{self.subscription.subject}"
        subject_parts = self.subject.rsplit(".", 2)
        self.labels = {
            "subject": subject_parts[0],
            "eventtype": subject_parts[1],
            "version": subject_parts[2],
        }
        EVENTS_WAITING.labels(**self.labels)
        EVENTS_WAITING_TIMEOUTS.labels(**self.labels)
        EVENTS_WAITING_TIME.labels(**self.labels)

        logger.info("Jetstream listening on %s", self.subject)
        logger.info("Using queue: %s", queue)

        self.psub = await self.js.pull_subscribe(
            subject=self.subject,
            durable=queue,
            stream=self.stream_name,
            config=self.subscription.config,
        )

        self.subscription.config = (await self.js._jsm.consumer_info(self.stream_name, queue)).config

    async def start(self) -> None:
        self.running = True

        reconnecting_process_task = asyncio.create_task(self._reconnect(self.process_queue))
        self.tasks.add(reconnecting_process_task)
        reconnecting_process_task.add_done_callback(self.tasks.discard)

        reconnecting_pull_task = asyncio.create_task(self._reconnect(self.pull_messages, self.psub))
        self.tasks.add(reconnecting_pull_task)
        reconnecting_pull_task.add_done_callback(self.tasks.discard)

    async def disconnect(self) -> None:
        self.running = False

        if hasattr(self, "message_queue"):
            # Signal queue to break out of their blocking .get() to prevent
            # hanging in case the queue was empty.
            self.message_queue.put_nowait((-1, ""))

    async def _reconnect(self, coro: Callable[..., Coroutine[Any, Any, None]], *args) -> None:
        """
        Wrapper around `coro` to manually trigger a NATS reconnect NATS when
        the connection gets in a closed state.
        """
        try:
            await coro(*args)
        except ConnectionClosedError:
            if self.running:
                # Prevent circular import.
                from service.injector import nats_connector

                await nats_connector.reconnect()

    async def pull_messages(self, psub) -> None:
        # Batch size starts high, but might drop to a low 10 over time to
        # better distribute events between pods. The high start is so any large
        # backlog of messages is consumed faster with as few pulls as possible.
        min_batch = 10
        max_batch = self.subscription.config.max_ack_pending // 10
        self.batch = max_batch
        fetch_history = deque(maxlen=10)

        # Timeout can be increased or decreased depending if the queue is
        # constantly empty or full.
        min_timeout = 0.01
        max_timeout = 1
        timeout = 0.1
        qsize_history = deque(maxlen=10)

        last_fetch = perf_counter()

        while self.running:
            while (last_qsize := self.message_queue.qsize()) >= self.batch * 0.2:
                # Let the queue be drained some more before pulling any more.
                logger.debug(
                    "Too many waiting, not pulling any more messages... queue size=%d, batch=%d",
                    last_qsize,
                    self.batch,
                )
                self.pull_event.clear()
                await self.pull_event.wait()

            now = perf_counter()

            try:
                # Fetch messages or wait until timeout, whichever comes first.
                # `len(msgs)` can exceed `batch`!
                msgs = await psub.fetch(self.batch, timeout=timeout)
            except TimeoutError:
                # Nothing to do.
                logger.debug("No messages available (in nats), timeout=%s, continuing...", timeout)
                await asyncio.sleep(0.01)
                timeout = min(timeout * 10, max_timeout)
            except ConnectionClosedError:
                # This can happen when the connection received unexpected
                # responses after a reconnect already happened automatically.
                # With the connection in a closed state, every `fetch()` will
                # raise this error.
                raise
            except Exception:
                # Wait after an exception has happened.
                logger.exception("An error happened during fetching NATS messages")
                await asyncio.sleep(1)
            else:
                logger.debug(
                    "Fetched %5d messages, queue size=%4d, batch=%4d, active=%3d, timeout=%.2f time since last fetch=%s",
                    len(msgs),
                    self.message_queue.qsize(),
                    self.batch,
                    self.active_tasks,
                    timeout,
                    now - last_fetch,
                )
                last_fetch = now

                # Reconsider `timeout`.
                last_qsize = self.message_queue.qsize()
                qsize_history.append(self.message_queue.qsize())
                if self.message_queue.qsize() == 0 and last_qsize == 0 and len(msgs) > 0:
                    timeout = max(timeout / 10, min_timeout)

                # Reconsider `batch`.
                fetch_history.append(len(msgs))
                if (sum(fetch_history) / len(fetch_history)) >= self.batch * 0.9:
                    self.batch = min(self.batch + 10, max_batch)
                    fetch_history.clear()
                elif len(fetch_history) >= 10:
                    self.batch = max(self.batch - 10, min_batch)

                EVENTS_WAITING.labels(**self.labels).inc(len(msgs))

                # Keep track of when these messages were pulled to have them
                # timeout when their ack_time has been exceeded.
                pull_time = perf_counter()
                for i, msg in enumerate(msgs, start=1):
                    self.message_queue.put_nowait((pull_time, msg))
                    if i % self.max_tasks == 0:
                        await asyncio.sleep(0)

    async def process_queue(self) -> None:
        ack_wait = self.subscription.config.ack_wait

        while self.running:
            pull_time, msg = await self.message_queue.get()

            # Check for exit condition.
            if pull_time == -1:
                self.message_queue.task_done()
                self.pull_event.set()
                break

            try:
                # Wait until active < max_tasks before continuing and
                # starting an asyncio task to process the message.
                time_queued = perf_counter() - pull_time
                remaining_ack_time = ack_wait - time_queued  # <= 0: immediate timeout
                async with asyncio.timeout(remaining_ack_time):
                    async with self.task_lock:
                        while self.running and self.active_tasks >= self.max_tasks:
                            await self.notify_lock.wait()
                        self.active_tasks += 1

                after_time = perf_counter()
                EVENTS_WAITING_TIME.labels(**self.labels).observe(after_time - pull_time)
            except TimeoutError:
                EVENTS_WAITING_TIMEOUTS.labels(**self.labels).inc()
                EVENTS_WAITING.labels(**self.labels).dec()
            else:
                EVENTS_WAITING.labels(**self.labels).dec()

                task = asyncio.create_task(self.subscription.on_message(msg))
                task.add_done_callback(self.tasks.discard)

                # Add task to the set. This creates a strong reference.
                self.tasks.add(task)

                # Cleanup/send signals when done.
                task.add_done_callback(
                    lambda task: asyncio.create_task(self._reconnect(self.on_message_done_callback, task)),
                )

    async def on_message_done_callback(self, task: asyncio.Task) -> None:
        if not task.cancelled() and (exc := task.exception()):
            # Re-raise, specifically to catch ConnectionClosedError.
            # This can happen when the connection received unexpected
            # responses after a reconnect already happened automatically.
            # With the connection in a closed state, every `ack()` will
            # raise this error.
            if isinstance(exc, ConnectionClosedError):
                raise exc
            else:
                logger.exception("Error in on_message", exc_info=exc)

        # Signal that any message that's waiting for a task slot can start.
        async with self.task_lock:
            self.active_tasks -= 1
            self.notify_lock.notify()

        # Signal the queue/pull task it might need to pull more messages.
        with contextlib.suppress(ValueError):
            self.message_queue.task_done()
        if (
            self.running
            and (last_qsize := self.message_queue.qsize()) < self.batch * 0.2
            and not self.pull_event.is_set()
        ):
            logger.debug(
                "Signaling pull task, queue size=%d, batch=%d, active=%d",
                last_qsize,
                self.batch,
                self.active_tasks,
            )
            self.pull_event.set()
