from enum import StrEnum, auto
from typing import Annotated, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, SecretStr


class RequestPerformerType(StrEnum):
    MACHINE = auto()
    USER = auto()


class RequestPerformer(BaseModel):
    id: UUID
    type: RequestPerformerType
    client_id: Annotated[UUID | None, BeforeValidator(lambda x: x or None)]
    partner_id: Annotated[UUID | None, BeforeValidator(lambda x: x or None)]
    original_token: SecretStr | None
    portal_partner_id: Annotated[UUID | None, BeforeValidator(lambda x: x or None)]
    portal_url: str | None
    wiki_url: str | None
    first_name: str | None
    preposition: str | None
    last_name: str | None


class BaseEntity(BaseModel):
    @classmethod
    def from_model(cls, model_object) -> Self:
        """
        Feel free to override if this does not cover your case.
        """
        return cls.model_validate(model_object)

    @classmethod
    def from_schema(cls, schema_object) -> Self:
        """
        Feel free to override if this does not cover your case.
        """
        return cls.model_validate(schema_object)

    def update(self, **kwargs) -> None:
        """
        Feel free to override if this does not cover your case.
        """
        for field_name, value in kwargs.items():
            setattr(self, field_name, value)

    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class EntityIdMixin(BaseModel):
    id: UUID = Field(default_factory=uuid4)
