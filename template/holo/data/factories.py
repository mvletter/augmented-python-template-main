from typing import Any, TypeVar

from polyfactory import AsyncPersistenceProtocol
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")


class AsyncPersistenceHandler(AsyncPersistenceProtocol[T]):
    __session: AsyncSession

    @classmethod
    def set_session(cls, session: AsyncSession) -> None:
        cls.__session = session

    @classmethod
    def reset_session(cls) -> None:
        del cls.__session

    async def save(self, data: T) -> T:
        self.__session.add(data)
        await self.__session.flush()

        relationships = []
        for relationship in inspect(data.__class__).relationships:
            relationships.append(relationship.key)

        await self.__session.refresh(data, relationships)
        return data

    async def save_many(self, data: list[T]) -> list[T]:
        self.__session.add_all(data)
        await self.__session.flush()

        for instance in data:
            relationships = []
            for relationship in inspect(instance.__class__).relationships:
                relationships.append(relationship.key)

            await self.__session.refresh(instance, relationships)
        return data


class BaseSQLAlchemyFactory(SQLAlchemyFactory[T]):
    """Base factory class for SQLAlchemy model creation.

    Provides functionality to manage the session and streamline the process
    of creating SQLAlchemy model instances. This class is designed to be
    used as a base factory for specific model factories, facilitating consistent
    session management for asynchronous SQLAlchemy operations.
    """

    __is_base_factory__ = True
    __set_relationships__ = False
    __async_persistence__ = AsyncPersistenceHandler

    __session: AsyncSession

    @classmethod
    def set_session(cls, session: AsyncSession) -> None:
        cls.__session = session

    @classmethod
    def reset_session(cls) -> None:
        del cls.__session

    @classmethod
    def build(cls, **kwargs: Any) -> T:
        instance = super().build(**kwargs)
        cls.__session.add(instance)
        return instance
