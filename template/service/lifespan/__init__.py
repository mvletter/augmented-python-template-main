from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from importlib import import_module
from importlib.util import find_spec
from typing import Protocol

from fastapi import FastAPI

from holo.config import config


class LifespanProtocol(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def __call__(self) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]: ...


if config.service.ENVIRONMENT:
    lifespan_module = config.service.ENVIRONMENT
else:
    local_spec = find_spec("service.lifespan.local")
    if local_spec:
        lifespan_module = "local"
    else:
        lifespan_module = "development"

module = import_module(f"service.lifespan.{lifespan_module}")
Lifespan: type[LifespanProtocol] = getattr(module, "Lifespan")
