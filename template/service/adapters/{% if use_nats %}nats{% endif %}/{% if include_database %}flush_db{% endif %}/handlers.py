import logging

from holo.nats.plain import NatsSubscriber
from service.adapters.nats.flush_db.events import FlushDbEvent
from service.core.usecases import FlushDbUsecase


flush_db_subscriber = NatsSubscriber()
logger = logging.getLogger(__name__)


@flush_db_subscriber.subscribe("local.flush_db.v1", FlushDbEvent)
@flush_db_subscriber.subscribe("staging.flush_db.v1", FlushDbEvent)
async def flush_db_handler(event: FlushDbEvent):
    """
    Drop and recreate the database.
    """
    logger.info("flush_db: start")

    await FlushDbUsecase()()  # this uses engine directly, no need for session

    logger.info("flush_db: done")
