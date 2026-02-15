import logging
from io import BufferedIOBase

from nats.js.api import ObjectStoreConfig
from nats.js.errors import BucketNotFoundError
from nats.js.object_store import ObjectStore

from holo.config import config
from holo.nats.client import HoloNats


logger = logging.getLogger(__name__)


class NatsObjectStore:
    """
    Used to retrieve files from the NATS object store.
    """

    def __init__(self, bucket: str) -> None:
        self.bucket: str = bucket
        self.object_store: ObjectStore

    async def connect(self, con: HoloNats, consumer_name: str) -> None:
        js_opts = {}
        if config.service.ENVIRONMENT and not config.service.TESTING:
            js_opts["domain"] = "voipgrid"
        js = con.jetstream(**js_opts)

        logger.info("Setting up object store %s.", self.bucket)
        # Create the object store if it doesn't exist yet.
        try:
            self.object_store = await js.object_store(self.bucket)
        except BucketNotFoundError:
            self.object_store = await js.create_object_store(
                bucket=self.bucket,
                config=ObjectStoreConfig(replicas=3),
            )

    async def start(self) -> None:
        """
        Not used by the object store but this class needs to conform to the interface defined by the plain NATS and
        stream subcribers.
        """

    async def disconnect(self) -> None:
        """
        Not used by the object store but this class needs to conform to the interface defined by the plain NATS and
        stream subcribers.
        """

    async def get(self, name: str, writeinto: BufferedIOBase) -> None:
        """
        Retrieve a file from the NATS object store and write its bytes to writeinto.
        """
        await self.object_store.get(name, writeinto)
