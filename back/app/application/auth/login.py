from dataclasses import dataclass

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.domain.user.repository import UserRepository
from app.infrastructure.cache.cache_service import CacheService


@dataclass
class LoginCommand:
    email: str
    password: str


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginUseCase:
    def __init__(self, user_repo: UserRepository, cache: CacheService):
        self._user_repo = user_repo
        self._cache = cache

    async def execute(self, cmd: LoginCommand) -> LoginResult:
        user = await self._user_repo.get_by_email(cmd.email)
        if not user or not verify_password(cmd.password, user.password):
            raise UnauthorizedError("이메일 또는 비밀번호가 올바르지 않습니다.")
        if not user.is_active:
            raise UnauthorizedError("비활성화된 계정입니다.")

        access_token, _ = create_access_token(user.id, user.role.value)
        refresh_token, refresh_jti = create_refresh_token(user.id)

        ttl = settings.JWT_REFRESH_EXPIRE_DAYS * 86400
        await self._cache.store_refresh_token(user.id, refresh_jti, ttl)

        return LoginResult(access_token=access_token, refresh_token=refresh_token)
