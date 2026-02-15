import asyncio
import inspect
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime, timedelta
from typing import Any

from holo.utils import SingletonMeta


class Check:
    def __init__(self, name: str, func: Callable[[], Coroutine[Any, Any, Any]], timeout: int | None = None) -> None:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("func must be a Coroutine (async def)")
        self.name = name
        self.func = func
        self.timeout = timeout

    async def run(self) -> None:
        if self.timeout:
            await asyncio.wait_for(self.func(), timeout=self.timeout)
        else:
            await self.func()


class HealthChecker:
    def __init__(self, checks: list[Check], timeout: int = 3, cache_ttl: int = 10) -> None:
        self.global_timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache_invalid_after = datetime.now(UTC)
        self._cache: dict[str, Any] = {}
        self._checks: list[Check] = []
        self._add_checks(checks)

    def _add_checks(self, checks: list[Check]) -> None:
        for check in checks:
            self._add_check(check)

    def _add_check(self, check: Check) -> None:
        if check.timeout is None:
            check.timeout = self.global_timeout
        self._checks.append(check)

    async def check(self, force_refresh: bool = False) -> dict[str, Any]:
        now = datetime.now(UTC)
        if self._cache_invalid_after > now and not force_refresh:
            return self._cache

        health_details: dict[str, Any] = {"status": "up", "details": {}}

        results = await asyncio.gather(
            *[check.run() for check in self._checks],
            return_exceptions=True,
        )

        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                error = str(result)
                health_details["status"] = "down"

                if isinstance(result, asyncio.TimeoutError):
                    error = f"check timed out after {self._checks[i].timeout} seconds"  # noqa
                elif error == "":
                    error = str(result.__class__)

                health_details["details"][self._checks[i].name] = {
                    "status": "down",
                    "error": error,
                }
            else:
                health_details["details"][self._checks[i].name] = {
                    "status": "up",
                }

        now = datetime.now(UTC)
        health_details["timestamp"] = now
        self._cache_invalid_after = now + timedelta(seconds=self.cache_ttl)
        self._cache = health_details

        return health_details


class SingletonHealthChecker(HealthChecker, metaclass=SingletonMeta):
    pass
