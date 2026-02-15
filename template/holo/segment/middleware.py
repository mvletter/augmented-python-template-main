import hashlib
import logging

from segment import analytics
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from holo.config import config
from holo.ctx import context


logger = logging.getLogger(__name__)


class SegmentASGIMiddleware:
    """
    Send events to segment if events were set in `context`.

    kwargs can be overwritten/amended from inside the view function context:

    ```
    from holo.ctx import context
    context.raw["segment"][kwarg] = value
    ```
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        context.raw["segment"] = {}

        # Convert headers to segment properties.
        segment_headers = {k[10:]: v for k, v in request.headers.items() if k.startswith("x-segment-")}

        # Separate identity, event, and context.
        segment_user_id = segment_headers.pop("user-id", None)
        segment_event = segment_headers.pop("event", None)
        segment_context = {}
        for name in list(segment_headers.keys()):
            if name.startswith("context-"):
                value = segment_headers.pop(name)
                parts = name.split("-")[1:]
                c = segment_context
                for i, part in enumerate(parts, start=1):
                    if part not in c and i < len(parts):
                        c[part] = {}
                        c = c[part]
                    else:
                        c[part] = value

        if segment_headers:
            logger.warning(
                "Discarded X-Segment headers: %s",
                ",".join(sorted(f"'{header}'" for header in segment_headers)),
            )

        if segment_user_id is None:
            try:
                vg_user_uuid = context.raw["jwt_dict"]["sub"]
                segment_user_id = hashlib.sha256(vg_user_uuid.encode()).hexdigest()
            except KeyError:
                segment_user_id = None
            except LookupError:
                raise ValueError(
                    "Cannot access `context.raw`. Make sure to check the relative "
                    "position to ASGIContextMiddleware in the order of middlewares.",
                )

        if segment_user_id:
            context.raw["segment"]["user_id"] = segment_user_id
        if segment_context:
            context.raw["segment"]["context"] = segment_context
        if (
            "context" not in context.raw["segment"]
            or "app" not in context.raw["segment"]["context"]
            or "name" not in context.raw["segment"]["context"]["app"]
        ):
            context.raw["segment"]["context"] = {"app": {"name": config.service.SERVICE_NAME}}
        if segment_event:
            context.raw["segment"]["event"] = segment_event

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                success = 200 <= message["status"] < 400
                if success and "event" in context.raw["segment"]:
                    try:
                        # .track() will queue an async request to segment,
                        # if we notice not all requests are sent, use
                        # .flush() to forcefully wait until queue is empty.
                        # It's not the default behavior (yet), since it
                        # noticeably slows down the response time.
                        analytics.track(**context.raw["segment"])
                        # analytics.flush()
                    except Exception as e:
                        logger.exception("Error occurred during send for Segment.", exc_info=e)
            await send(message)

        await self.app(scope, receive, send_wrapper)
