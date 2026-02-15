"""
This is a generic models file. This contain model logic that is
shared across modules.
"""

from typing import Self

from sqlalchemy import Column, MetaData, func, inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import MANYTOMANY, MANYTOONE, ONETOMANY, as_declarative


metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s_%(column_1_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


@as_declarative(metadata=metadata)
class BaseSqlModel:
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, server_default=func.gen_random_uuid())

    @classmethod
    def from_entity(cls, entity_object) -> Self:
        """
        Feel free to override if this does not cover your case.
        """
        data = entity_object.model_dump()

        for rel in inspect(cls).relationships:
            local_field = rel.key
            if local_field in data and data[local_field]:
                remote_class = rel.entity.entity
                # Turn relation dict -> Model.
                if rel.direction == MANYTOONE:
                    data[local_field] = remote_class.from_entity(getattr(entity_object, local_field))
                # Turn relation list -> list[Model].
                elif rel.direction in [ONETOMANY, MANYTOMANY]:
                    data[local_field] = list(map(remote_class.from_entity, getattr(entity_object, local_field)))

        return cls(**data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (id={self.id})>"
