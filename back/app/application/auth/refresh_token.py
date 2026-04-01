from dataclasses import dataclass

from jose import JWTError

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, decode_token
from app.domain.user.repository import UserRepository
from app.infrastructure.cache.cache_service import CacheService


@dataclass
class RefreshResult:
    access_token: str
    token_type: str = "bearer"


class RefreshTokenUseCase:
    def __init__(self, user_repo: UserRepository, cache: CacheService):
        self._user_repo = user_repo
        self._cache = cache

    async def execute(self, refresh_token: str) -> RefreshResult:
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise UnauthorizedError("유효하지 않은 리프레시 토큰입니다.")

        if payload.get("type") != "refresh":
            raise UnauthorizedError()

        user_id = int(payload["sub"])
        jti = payload.get("jti")

        if not jti or not await self._cache.refresh_token_exists(user_id, jti):
            raise UnauthorizedError("만료되거나 로그아웃된 토큰입니다.")

        user = await self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError()

        access_token, _ = create_access_token(user.id, user.role.value)
        return RefreshResult(access_token=access_token)
