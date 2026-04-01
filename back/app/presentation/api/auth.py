from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.login import LoginCommand, LoginUseCase
from app.application.auth.logout import LogoutCommand, LogoutUseCase
from app.application.auth.refresh_token import RefreshTokenUseCase
from app.application.auth.register import RegisterCommand, RegisterUseCase
from app.infrastructure.cache.cache_service import CacheService
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.user_repo import SQLUserRepository
from app.presentation.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.presentation.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


def _cache(redis=Depends(get_redis)) -> CacheService:
    return CacheService(redis)


@router.post("/register", response_model=ApiResponse[RegisterResponse], status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    use_case = RegisterUseCase(SQLUserRepository(db))
    result = await use_case.execute(RegisterCommand(email=body.email, password=body.password, name=body.name, phone=body.phone))
    return ApiResponse(data=RegisterResponse(id=result.id, email=result.email, name=result.name))


@router.post("/login", response_model=ApiResponse[LoginResponse])
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db), cache: CacheService = Depends(_cache)):
    use_case = LoginUseCase(SQLUserRepository(db), cache)
    result = await use_case.execute(LoginCommand(email=body.email, password=body.password))
    return ApiResponse(data=LoginResponse(access_token=result.access_token, refresh_token=result.refresh_token))


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    authorization: str = Header(...),
    cache: CacheService = Depends(_cache),
):
    token = authorization[7:] if authorization.startswith("Bearer ") else ""
    use_case = LogoutUseCase(cache)
    await use_case.execute(LogoutCommand(access_token=token, refresh_token=body.refresh_token))
    return ApiResponse(data={"message": "로그아웃 완료"})


@router.post("/refresh", response_model=ApiResponse[RefreshResponse])
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db), cache: CacheService = Depends(_cache)):
    use_case = RefreshTokenUseCase(SQLUserRepository(db), cache)
    result = await use_case.execute(body.refresh_token)
    return ApiResponse(data=RefreshResponse(access_token=result.access_token))
