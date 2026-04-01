from datetime import datetime, timezone

from fastapi import Request
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_token
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis


class ActivityTrackerMiddleware(BaseHTTPMiddleware):
    """인증된 요청마다 MAU(Monthly Active Users)를 Redis에 추적하는 미들웨어."""

    async def dispatch(self, request: Request, call_next):
        # Authorization 헤더에서 user_id 추출 (실패해도 요청은 정상 처리)
        user_id = self._extract_user_id(request)
        if user_id is not None:
            try:
                redis = await get_redis()
                cache = CacheService(redis)
                year_month = datetime.now(timezone.utc).strftime("%Y-%m")
                await cache.track_mau(year_month, user_id)
            except Exception:
                # MAU 추적 실패는 요청 처리에 영향 없음
                pass

        return await call_next(request)

    @staticmethod
    def _extract_user_id(request: Request) -> int | None:
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None
        token = authorization[7:]
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                return None
            sub = payload.get("sub")
            return int(sub) if sub else None
        except (JWTError, ValueError, TypeError):
            return None
