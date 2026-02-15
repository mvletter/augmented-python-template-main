import math
from typing import Any, Self, cast
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class BaseSchema(BaseModel):
    @classmethod
    def from_entity(cls, entity_object: BaseModel) -> Self:
        """
        Feel free to override if this does not cover your case.
        """
        return cls.model_validate(entity_object)

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", from_attributes=True)


class SchemaIdMixin(BaseModel):
    id: UUID


class ErrorDetail(BaseModel):
    loc: list[str]
    type: str
    msg: str
    # Commented for now, might enable in the future.
    # ctx: dict | None


class ValidationErrorSchema(BaseModel):
    detail: ErrorDetail


class ClientErrorSchema(BaseModel):
    detail: Any = None


class ProblemSchema(BaseModel):
    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None

    @field_validator("status")
    def status_max(cls, value: int) -> int:
        assert value <= 600
        return value

    @field_validator("status")
    def status_min(cls, value: int) -> int:
        assert value >= 100
        return value


class PaginatedSchema(BaseModel):
    """
    Create your own subschema for a more specific schema for `items:`.

    ```
    class MyFirstListSchema(PaginatedSchema):
        items: list[MyFirstSchema] = []
    ```

    Example use in a view:
    ```
    async def get_timebasedrouting_list(
        request: Request,
        page: int = None,
        per_page: PerPageEnum = None,
        repository: Repository = Depends(repository),
    ) -> MyFirstListSchema:

        items, page, per_page, total = await repository.list_paginated(
            page,
            per_page,
        )

        return MyFirstListSchema(
            **MyFirstListSchema.build_values(
                str(request.url),
                page,
                per_page,
                total,
                items=list(map(MyFirstSchema.from_entity, items)),
                original_uri=request.headers.get("x-original-uri"),
            )
        )
    ```
    """

    self: str
    first: str
    prev: str
    next: str | None
    last: str
    count: int
    query: dict
    items: list[BaseModel] = []

    @classmethod
    def build_values(cls, self_url, page, per_page, total, items, original_uri) -> dict[str, Any]:
        values = {"items": items}

        # Generate prev/next and first/last urls based on `self_url`.
        parts = urlparse(self_url)
        base_parts = parts._replace(query="")

        # Keep netloc + path-prefix from original_uri.
        if original_uri:
            original_parts = urlparse(original_uri)
            base_parts = base_parts._replace(scheme=original_parts.scheme)
            base_parts = base_parts._replace(netloc=original_parts.netloc)
            if original_parts.path != base_parts.path:
                path_prefix = original_parts.path.removesuffix(base_parts.path)
                base_parts = base_parts._replace(path=f"{path_prefix}{base_parts.path}")

        # Unpack single-value params so {page: ["1"]} becomes {page: "1"}.
        qs = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in parse_qs(parts.query).items()}
        if not qs.get("page"):
            qs["page"] = page
        if not qs.get("per_page"):
            qs["per_page"] = per_page

        # Repack self_url, this also adds page/per_page if they were omitted.
        self_qs = {**qs, "page": page}  # page might've changed after validation
        self_parts = base_parts._replace(query=urlencode(self_qs))
        values["self"] = urlunparse(self_parts)

        # Set page = first.
        first_qs = {**qs, "page": 1}
        first_parts = base_parts._replace(query=urlencode(first_qs))
        values["first"] = urlunparse(first_parts)

        # Set page = last.
        last_page = math.ceil(max(total, 1) / per_page)
        last_qs = {**qs, "page": last_page}
        last_parts = base_parts._replace(query=urlencode(last_qs))
        values["last"] = urlunparse(last_parts)

        # Set prev page = self - 1.
        prev_page = max(int(cast(str, qs.get("page") or "2")) - 1, 1)
        prev_qs = {**qs, "page": prev_page}
        prev_parts = base_parts._replace(query=urlencode(prev_qs))
        values["prev"] = urlunparse(prev_parts)

        # Set next page = self + 1, *if* there is a next.
        next_page = int(cast(str, qs.get("page") or "1")) + 1
        if next_page > last_page:
            values["next"] = None
        else:
            next_qs = {**qs, "page": next_page}
            next_parts = base_parts._replace(query=urlencode(next_qs))
            values["next"] = urlunparse(next_parts)

        # Add search params without page parameters.
        qs.pop("page", None)
        qs.pop("per_page", None)
        values["query"] = qs

        # Add total item count.
        values["count"] = total

        return values
