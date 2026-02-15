"""
Module to manage context shared across interactions without the need
to synchronize everything yourself.

Inspired by: https://github.com/tomwojcik/starlette-context

"""

import logging
from contextvars import ContextVar
from http import HTTPStatus
from typing import Any

import aiohttp
import jwt
from aiocache import cached
from jwt.exceptions import DecodeError
from starlette.datastructures import Headers
from starlette.responses import PlainTextResponse
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential

from holo.config import config
from holo.core.entities import RequestPerformer


# Automatically scoped context.
_holo_service_context: ContextVar[dict[Any, Any]] = ContextVar("holo_service_context")
logger = logging.getLogger(__name__)


class _Context:
    """
    Class for easier access of underlying ContextVar.
    """

    @property
    def raw(self) -> dict:
        try:
            return _holo_service_context.get()
        except LookupError:
            raise

    @property
    def request_performer(self) -> RequestPerformer | None:
        if jwt_dict := self.raw.get("jwt_dict"):
            return RequestPerformer(
                id=jwt_dict["sub"],
                type=jwt_dict["type"],
                client_id=jwt_dict["client_id"],
                partner_id=jwt_dict["partner_id"],
                original_token=jwt_dict["original_token"],
                portal_partner_id=jwt_dict.get("portal_partner_id"),
                portal_url=jwt_dict.get("portal_url"),
                wiki_url=jwt_dict.get("wiki_url"),
                first_name=jwt_dict.get("first_name"),
                preposition=jwt_dict.get("preposition"),
                last_name=jwt_dict.get("last_name"),
            )
        return None

    @property
    def auth_header(self) -> str:
        return self.raw.get("auth_header") or ""


context = _Context()


class ASGIContextMiddleware:
    def __init__(self, app):
        self.app = app

    @property
    @cached(ttl=300)
    async def jwk_set(self) -> jwt.PyJWKSet | None:
        try:
            jwks = await self.__get_jwk_set()
            return jwks
        except RetryError:
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=1, max=10))
    async def __get_jwk_set(self) -> jwt.PyJWKSet | None:
        """
        Get public key certificates (jwks) from auth service who signed the encoded JWT.
        """
        if config.service.AUTH_BASE_URL:
            jwks_url = f"{config.service.AUTH_BASE_URL}/jwks"
            try:
                async with aiohttp.request("GET", jwks_url) as response:
                    response.raise_for_status()
                    certificates = await response.json()
                    jwks = jwt.PyJWKSet.from_dict(certificates)
            except Exception:
                logger.exception("Failed to get jwks from %s", jwks_url)
                raise
            else:
                return jwks

    @cached()
    async def __get_jwk(self, kid: str) -> jwt.PyJWK:
        """
        Return the jwk for the requested kid.
        """
        jwk_set = await self.jwk_set
        try:
            jwk = jwk_set[kid]
        except KeyError:
            logger.error("There is no jwk available for token with kid: %s", kid)
            raise DecodeError
        else:
            return jwk

    @staticmethod
    def __get_token_from_header(scope) -> str:
        headers = Headers(scope=scope)
        auth_header = headers.get("authorization", None)

        if not auth_header:
            return ""

        try:
            scheme, encoded_token = auth_header.split()
        except ValueError:
            raise DecodeError

        if scheme.lower() != "bearer":
            raise DecodeError

        return encoded_token

    async def decode_token(self, encoded_token: str) -> Any:
        """
        Decode encoded JWT token.
        """
        if await self.jwk_set:
            try:
                kid = jwt.get_unverified_header(encoded_token).get("kid")
                jwk = await self.__get_jwk(kid)

                return jwt.decode(encoded_token, jwk, leeway=10)
            except Exception as e:
                logger.exception(e)
                raise DecodeError
        else:
            # No jwks available so we skip signature verification.
            return jwt.decode(encoded_token, options={"verify_signature": False}, leeway=10)

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        ctx = {}
        try:
            if encoded_token := self.__get_token_from_header(scope):
                ctx["auth_header"] = f"Bearer {encoded_token}"
                ctx["jwt_dict"] = await self.decode_token(encoded_token)  # Raises DecodeError.
        except DecodeError:
            response = PlainTextResponse(
                "malformed Authorization header, use: Bearer ENCODED_JWT_TOKEN",
                status_code=HTTPStatus.BAD_REQUEST.value,
            )
            await response(scope, receive, send)
        else:
            token = _holo_service_context.set(ctx)
            try:
                await self.app(scope, receive, send)
            finally:
                _holo_service_context.reset(token)
