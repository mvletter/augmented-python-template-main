import json
from collections.abc import Awaitable, Callable
from typing import TypeVar

from nats.aio.msg import Msg

from holo.nats.client import HoloNats
from holo.resclient.models import AccessResGateModel, BaseResGateModel, GetResGateModel
from holo.utils import to_json_string


T = TypeVar("T")
type ResGateAccessCallback = Callable[[AccessResGateModel], Awaitable[bool]]
type ResGateGetCallback = Callable[[GetResGateModel], Awaitable[bool]]


class Handler[T: BaseResGateModel]:
    _subject: str
    _model: type[T]

    async def connect(self, nc: HoloNats) -> None:
        """
        Subscribe to topic and set callback for incoming events.
        """
        self._nats_connection = nc
        await self._nats_connection.subscribe(self._subject, queue=self._subject, cb=self._handle_request)

    def _get_id(self, subject: str) -> str:
        """
        Get the id of the subject.
        """
        last_dot_index = subject.rfind(".")
        return subject[last_dot_index + 1 :]

    async def _handle_request(self, msg: Msg) -> None:
        """
        Callback that is called for each ResGate request.
        """
        model = self._model(
            subject=msg.subject,
            reply=msg.reply,
            data=json.loads(msg.data),
            id=self._get_id(msg.subject),
        )
        response = await self._process(model)

        headers = msg.headers or {}
        await self._nats_connection.publish(
            msg.reply,
            json.dumps(
                response,
                default=to_json_string,
            ).encode(),
            headers=headers,
        )

    async def _process(self, model: T) -> dict:
        raise NotImplementedError


class GetHandler(Handler[GetResGateModel]):
    """
    Handler for Get requests.
    """

    _model = GetResGateModel

    def __init__(self, subject: str, callback: ResGateGetCallback) -> None:
        self._subject = f"get.{subject}"
        self._callback = callback

    async def _process(self, model: GetResGateModel) -> dict:
        """
        Process incoming event and return valid Get response.
        """
        response = await self._callback(model)

        if response:
            assert isinstance(response, dict), "Response from get handler should be a dict."

            return {"result": response}
        else:
            return {"error": {"code": "system.notFound", "message": "Not found"}}


class AccessHandler(Handler[AccessResGateModel]):
    """
    Handler for Access requests.
    """

    _model = AccessResGateModel

    def __init__(self, subject: str, callback: ResGateAccessCallback) -> None:
        self._subject = f"access.{subject}"
        self._callback = callback

    async def _process(self, model: AccessResGateModel) -> dict:
        """
        Process incoming event and return valid Access response.
        """
        response = await self._callback(model)

        assert isinstance(response, bool), "Response from access handler should be a boolean."

        return {"result": {"get": response, "call": ""}}
