import inspect
from collections.abc import Awaitable, Callable
from functools import wraps
from time import perf_counter

from prometheus_client import Counter, Gauge, Histogram
from prometheus_client.utils import INF

from holo.nats.exceptions import NakException


EVENTS = Counter(
    "nats_events_total",
    "Total count of NATS events by eventtype, subject and version",
    ["subject", "eventtype", "version"],
)
EVENTS_PROCESSING_TIME = Histogram(
    "nats_time_seconds",
    "Histogram of NATS events processing time by event (in seconds)",
    ["subject", "eventtype", "version"],
)
EVENTS_DELAY = Gauge(
    "nats_events_delay",
    "Gauge of NATS events consumer delay by eventtype, subject and version",
    ["subject", "eventtype", "version"],
)
EXCEPTIONS = Counter(
    "nats_exceptions_total",
    "Total count of exceptions raised by eventtype, subject and version",
    ["subject", "eventtype", "version"],
)
EVENTS_ACK_TIMEOUTS = Counter(
    "nats_ack_timeouts_total",
    "Total count of ack timeouts caused by slow handlers",
    ["subject", "eventtype", "version"],
)
EVENTS_IN_PROGRESS = Gauge(
    "nats_events_in_progress",
    "Gauge of NATS events by eventtype, subject and version currently being processed",
    ["subject", "eventtype", "version"],
)
EVENT_NAKS = Counter(
    "nats_events_nak_total",
    "Total count of NATS events NAK'ed by eventtype, subject and version",
    ["subject", "eventtype", "version"],
)


EVENTS_WAITING_TIME = Histogram(
    "nats_waiting_time_seconds",
    "Histogram of NATS events waiting time before being processed by event (in seconds)",
    ["subject", "eventtype", "version"],
    buckets=(
        0.001,
        0.002,
        0.003,
        0.004,
        0.005,
        0.01,
        0.02,
        0.03,
        0.04,
        0.05,
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        10.0,
        20.0,
        30.0,
        INF,
    ),
)
EVENTS_WAITING_TIMEOUTS = Counter(
    "nats_waiting_timeouts_total",
    "Total count of waiting timeouts by event",
    ["subject", "eventtype", "version"],
)
EVENTS_WAITING = Gauge(
    "nats_events_waiting",
    "Gauge of NATS events by eventtype, subject and version currently waiting before being processed by event",
    ["subject", "eventtype", "version"],
)


def instrument(
    subject: str,
    eventtype: str,
    version: str,
    ack_wait=30,
) -> Callable[[Callable[..., Awaitable]], Callable[..., Awaitable]]:
    """
    Decorator to add instrumentation to our handlers.

    It provides:
        - EVENTS
        - EVENTS_PROCESSING_TIME
        - EXCEPTIONS
        - EVENTS_ACK_TIMEOUTS
        - EVENTS_IN_PROGRESS

    'instrument' wraps the actual decorator to provide extra parameters.

    Usage: @instrument("subject", "eventtype", "version")

    Args:
        subject (str): Subject being instrumented, ie. "PORTAL.phoneaccount".
        eventtype (str): Type of event ("created", "changed", "deleted", etc).
        version (str): Version of the event, ie. "v1".
        ack_wait (int): Time in seconds NATS will wait for a consumer to ACK
            an event - this can be changed per consumer.

    Returns:
        coroutine: function wrapper which will count the number of events as well as time the
            amount of time it takes to process an event.
    """
    # Initialize the labels.
    EVENTS.labels(subject=subject, eventtype=eventtype, version=version)
    EVENTS_DELAY.labels(subject=subject, eventtype=eventtype, version=version)
    EVENTS_PROCESSING_TIME.labels(subject=subject, eventtype=eventtype, version=version)
    EXCEPTIONS.labels(subject=subject, eventtype=eventtype, version=version)
    EVENTS_ACK_TIMEOUTS.labels(subject=subject, eventtype=eventtype, version=version)
    EVENTS_IN_PROGRESS.labels(subject=subject, eventtype=eventtype, version=version)
    EVENT_NAKS.labels(subject=subject, eventtype=eventtype, version=version)
    EVENTS_WAITING_TIMEOUTS.labels(subject=subject, eventtype=eventtype, version=version)
    EVENTS_WAITING.labels(subject=subject, eventtype=eventtype, version=version)

    def inner(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        if not inspect.iscoroutinefunction(func):
            raise Exception(f"Function {func.__name__} must be declared async to use with the @instrument decorator")

        @wraps(func)
        async def wrapper(event, *args, **kwargs) -> Awaitable:
            EVENTS_IN_PROGRESS.labels(subject=subject, eventtype=eventtype, version=version).inc()
            EVENTS.labels(subject=subject, eventtype=eventtype, version=version).inc()
            if hasattr(event, "time"):
                EVENTS_DELAY.labels(subject=subject, eventtype=eventtype, version=version).set(
                    float(event.time.timestamp()),
                )
            before_time = perf_counter()
            try:
                ret = await func(event, *args, **kwargs)
            except NakException:
                # raise without doing EXCEPTIONS.inc(), elsewhere
                # EVENT_NAKS will be incremented.
                raise
            except BaseException:
                EXCEPTIONS.labels(subject=subject, eventtype=eventtype, version=version).inc()
                raise
            else:
                after_time = perf_counter()
                EVENTS_PROCESSING_TIME.labels(subject=subject, eventtype=eventtype, version=version).observe(
                    after_time - before_time,
                )
                if after_time - before_time > ack_wait:
                    EVENTS_ACK_TIMEOUTS.labels(subject=subject, eventtype=eventtype, version=version).inc()
                return ret
            finally:
                EVENTS_IN_PROGRESS.labels(subject=subject, eventtype=eventtype, version=version).dec()

        return wrapper

    return inner
