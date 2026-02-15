from typing import Any

from fastapi import HTTPException as FastapiHTTPException


EXCEPTIONS_MAPPER_4XX = {
    400: "bad_request",
    401: "not_authenticated",
    403: "permission_denied",
    404: "not_found",
    405: "method_not_allowed",
    406: "not_acceptable",
    408: "request_timeout",
    409: "conflict",
    410: "gone",
    412: "precondition_failed",
    415: "unsupported_media_type",
    423: "locked",
    428: "precondition_required",
    429: "too_many_requests",
}


class HTTPException(FastapiHTTPException):
    """
    Subclass FastApi's HTTPException to add `error_code`.

    You can define a custom `error_code` which will be used or the default code
    corresponding to the status_code will be mapped and used instead.
    """

    error_code: str | None = None

    def __init__(
        self,
        status_code: int,
        error_code: str | None = None,
        detail: Any = None,
        headers: dict[str, Any] | None = None,
    ) -> None:
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=detail, headers=headers)
