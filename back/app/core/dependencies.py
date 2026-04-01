from fastapi import Depends, Header
from jose import JWTError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.database import get_db


async def get_current_user_id(
    authorization: str = Header(...),
    redis: Redis = Depends(get_redis),
) -> int:
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError()
    token = authorization[7:]
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedError("유효하지 않은 토큰입니다.")

    if payload.get("type") != "access":
        raise UnauthorizedError("액세스 토큰이 아닙니다.")

    jti = payload.get("jti")
    if jti and await redis.exists(f"blacklist:access:{jti}"):
        raise UnauthorizedError("로그아웃된 토큰입니다.")

    return int(payload["sub"])


async def get_current_user_payload(
    authorization: str = Header(...),
    redis: Redis = Depends(get_redis),
) -> dict:
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError()
    token = authorization[7:]
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedError("유효하지 않은 토큰입니다.")

    if payload.get("type") != "access":
        raise UnauthorizedError("액세스 토큰이 아닙니다.")

    jti = payload.get("jti")
    if jti and await redis.exists(f"blacklist:access:{jti}"):
        raise UnauthorizedError("로그아웃된 토큰입니다.")

    return payload


async def require_admin(
    payload: dict = Depends(get_current_user_payload),
) -> dict:
    if payload.get("role") != "admin":
        raise ForbiddenError("관리자 권한이 필요합니다.")
    return payload
