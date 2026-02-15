import json
import logging
from collections.abc import Callable

from holo.config.resclient import ResgateConfig
from holo.data.connectors import NatsConnector
from holo.nats.client import HoloNats
from holo.resclient.handlers import AccessHandler, GetHandler, Handler, ResGateAccessCallback, ResGateGetCallback
from holo.utils import to_json_string


logger = logging.getLogger(__name__)


class ResClient:
    """
    ResClient to easily communicate with ResGate over Nats.
    """

    def __init__(self, connector: NatsConnector, config: ResgateConfig) -> None:
        self._enabled = config.ENABLE_RESGATE
        self._connector = connector
        self._handlers: list[Handler] = []
        self._nats_connection: HoloNats

    async def startup(self) -> None:
        logger.info("Starting ResClient")
        self._nats_connection = await self._connector.new_connection()

        for handler in self._handlers:
            await handler.connect(self._nats_connection)

    async def shutdown(self) -> None:
        await self._connector.close_connection()

    def get(self, subject: str) -> Callable:
        """
        Decorator for GET requests.

        Usage:
        @client.get("foo.bar")
        async def get_foo_bar(model: GetResGateModel) -> dict:
            ...
            return {"model": {"foo": "bar"}}
        """

        def get_handler(cb: ResGateGetCallback) -> ResGateGetCallback:
            self._handlers.append(GetHandler(subject, cb))

            return cb

        return get_handler

    def access(self, subject: str) -> Callable:
        """
        Decorator for ACCESS requests.

        Usage:

        ```
        @client.access("foo.bar")
        async def access_foo_bar(model: AccessResGateModel) -> bool:
            ...
            return True / False
        ```
        """

        def access_handler(cb: ResGateAccessCallback) -> ResGateAccessCallback:
            self._handlers.append(AccessHandler(subject, cb))

            return cb

        return access_handler

    async def _publish(
        self,
        subject: str,
        payload: dict | None,
        headers=None,
    ) -> None:
        """
        Proxy function to self._nc.publish for easy instrumentation.
        """
        if self._enabled:
            kwargs = {
                "subject": subject,
                "headers": headers,
            }

            if payload:
                kwargs["payload"] = json.dumps(payload, default=to_json_string).encode()

            await self._nats_connection.publish(**kwargs)

    async def event_change(
        self,
        resource_id: str,
        data: dict,
        headers=None,
    ) -> None:
        """
        Publish a change event for the given resource_id.
        """
        await self._publish(f"event.{resource_id}.change", {"values": data}, headers=headers)

    async def system_reset(
        self,
        data: list[str],
        headers=None,
    ) -> None:
        """
        Publish a system reset event for the given resource.
        """
        await self._publish("system.reset", {"resources": data}, headers=headers)

    async def event_add_rid_to_collection(
        self,
        collection_resource_id: str,
        added_resource_id: str,
        added_idx: int,
        headers=None,
    ) -> None:
        """
        Publish a new RID being added to a collection.
        """
        await self._publish(
            f"event.{collection_resource_id}.add",
            {"idx": added_idx, "value": {"rid": added_resource_id}},
            headers=headers,
        )

    async def event_remove_item_from_collection(
        self,
        collection_resource_id: str,
        removed_idx: int,
        headers=None,
    ) -> None:
        """
        Publish a remove event for the given resource_id.
        """
        await self._publish(f"event.{collection_resource_id}.remove", {"idx": removed_idx}, headers=headers)

    async def event_delete(
        self,
        resource_id: str,
        headers=None,
    ) -> None:
        """
        Publish a delete event for the given resource_id.
        """
        await self._publish(f"event.{resource_id}.delete", None, headers=headers)
