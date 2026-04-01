from datetime import datetime, timezone, timedelta
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _make_token(data: dict, expire_delta: timedelta) -> tuple[str, str]:
    """토큰 생성. (token, jti) 반환."""
    jti = str(uuid4())
    payload = {
        **data,
        "jti": jti,
        "exp": datetime.now(timezone.utc) + expire_delta,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token, jti


def create_access_token(user_id: int, role: str) -> tuple[str, str]:
    return _make_token(
        {"sub": str(user_id), "role": role, "type": "access"},
        timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> tuple[str, str]:
    return _make_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """토큰 디코딩. 유효하지 않으면 JWTError 발생."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
