import asyncio

import pytest

from holo.health import Check, HealthChecker


async def test_timeout() -> None:
    """
    Check health checker times out after 1 second.
    """

    async def time_me_out() -> None:
        await asyncio.sleep(2)

    timeout_check = Check("timeout", time_me_out, timeout=1)
    checker = HealthChecker(checks=[timeout_check])

    result = await checker.check()

    assert result["status"] == "down"
    assert result["details"]["timeout"]["status"] == "down"
    assert result["details"]["timeout"]["error"] == "check timed out after 1 seconds"


async def test_cache() -> None:
    """
    Test health checked uses caching.
    """

    async def some_check() -> None:
        await asyncio.sleep(0.1)

    check = Check("some-check", some_check)
    checker = HealthChecker(checks=[check], cache_ttl=2)

    result = await checker.check()

    await asyncio.sleep(0.1)

    next_result = await checker.check()

    assert result["timestamp"] == next_result["timestamp"]


def test_only_async_func() -> None:
    """
    Test health check only accepts async functions.
    """

    def not_an_async_check() -> None:
        pass

    with pytest.raises(TypeError):
        Check(name="not-async", func=not_an_async_check)  # type: ignore[arg-type]
