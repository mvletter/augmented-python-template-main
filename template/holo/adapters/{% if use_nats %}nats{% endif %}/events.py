from time import mktime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict


class BaseEvent(BaseModel):
    """
    Base model for events.
    """

    uuid: UUID
    name: str
    time: AwareDatetime
    payload: dict | None = None

    @property
    def timestamp(self) -> int:
        """
        Create an epoch timestamp from the event time.
        """
        return int(mktime(self.time.utctimetuple()))

    model_config = ConfigDict(extra="ignore", use_enum_values=True)
