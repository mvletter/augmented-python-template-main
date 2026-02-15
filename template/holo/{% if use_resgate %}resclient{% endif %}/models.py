from typing import Any

from pydantic import BaseModel


class BaseResGateModel(BaseModel):
    """
    Base model with fields that are always present in events from ResGate.
    """

    subject: str
    reply: str
    id: str
    data: Any


class GetResGateModel(BaseResGateModel):
    """
    Model to handle GET requests from Resgate. Data is always a dict and can
    contain anything.
    """

    data: dict


class AccessResGateModel(BaseResGateModel):
    """
    Model to handle ACCESS requests from Resgate. Data contains a token field
    that can contain anything and the cid (connection id).
    """

    class Data(BaseModel):
        token: dict | None = None
        cid: str

    data: Data
