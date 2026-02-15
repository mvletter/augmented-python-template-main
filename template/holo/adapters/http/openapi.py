from typing import Any

from holo.adapters.http.schemas import ClientErrorSchema, ValidationErrorSchema


type OpenApiResponse = dict[int | str, dict[str, Any]]


# Supporting https://opensource.zalando.com/restful-api-guidelines/#176
default_response: OpenApiResponse = {
    "default": {
        "description": "Unknown Error",
        "content": {
            "application/problem+json": {
                "schema": {
                    "$ref": "https://voipgrid.github.io/restful-api-guidelines/problem-1.0.1.yaml#/Problem",
                },
            },
        },
    },
}

validation_error_response: OpenApiResponse = {
    400: {"description": "Validation Error", "model": ValidationErrorSchema},
}

not_found_error_response: OpenApiResponse = {
    404: {"description": "Not Found", "model": ClientErrorSchema},
}
