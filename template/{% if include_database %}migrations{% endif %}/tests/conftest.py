import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from holo.testing.fixtures import create_async_engine, create_database


@pytest.fixture
async def alembic_engine(database_url) -> AsyncEngine:
    """
    Use a separate database for pytest_alembic to test migrations.
    """
    db_url = database_url
    test_db_url = db_url.set(database=f"{db_url.database}_migrations")

    await create_database(test_db_url)

    return create_async_engine(test_db_url)
