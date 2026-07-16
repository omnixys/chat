from __future__ import annotations

import asyncio
from dataclasses import dataclass

import jwt
from fastapi import HTTPException, Request, WebSocket, status
from jwt import PyJWKClient

from chat.config import settings


@dataclass(frozen=True)
class Principal:
    user_id: str
    username: str = ""


_jwks_client: PyJWKClient | None = None


def _token_from_connection(
    connection: Request | WebSocket,
    connection_params: object | None = None,
) -> str:
    authorization = connection.headers.get("authorization", "")
    if isinstance(connection_params, dict):
        authorization = str(
            connection_params.get("Authorization")
            or connection_params.get("authorization")
            or authorization
        )
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    if isinstance(connection_params, dict):
        token = connection_params.get("accessToken") or connection_params.get("token")
        if isinstance(token, str) and token:
            return token.removeprefix("Bearer ").strip()
    return connection.cookies.get("access_token", "")


async def authenticate_connection(
    connection: Request | WebSocket,
    connection_params: object | None = None,
) -> Principal:
    if not settings.auth_enabled:
        user_id = connection.headers.get("x-test-user-id", "test-user")
        return Principal(user_id=user_id, username=user_id)

    token = _token_from_connection(connection, connection_params)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
        )

    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(settings.keycloak.jwks_url, cache_keys=True)
    try:
        signing_key = await asyncio.to_thread(_jwks_client.get_signing_key_from_jwt, token)
        options: dict[str, bool] = {"verify_aud": bool(settings.keycloak.audience)}
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.keycloak.issuer,
            audience=settings.keycloak.audience or None,
            options=options,  # type: ignore[arg-type]
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid access token"
        ) from exc
    user_id = str(payload.get("sub", ""))
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token subject missing",
        )
    return Principal(user_id=user_id, username=str(payload.get("preferred_username", "")))
