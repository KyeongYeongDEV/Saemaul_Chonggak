from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.exceptions import DuplicateEmailError
from app.core.security import hash_password
from app.domain.user.entities import User, UserRole
from app.domain.user.repository import UserRepository


@dataclass
class RegisterCommand:
    email: str
    password: str
    name: str
    phone: str | None


@dataclass
class RegisterResult:
    id: int
    email: str
    name: str


class RegisterUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, cmd: RegisterCommand) -> RegisterResult:
        existing = await self._user_repo.get_by_email(cmd.email)
        if existing:
            raise DuplicateEmailError()

        user = User(
            id=None,
            email=cmd.email,
            password=hash_password(cmd.password),
            name=cmd.name,
            phone=cmd.phone,
            role=UserRole.USER,
            is_active=True,
            point=0,
            created_at=datetime.now(timezone.utc),
        )
        saved = await self._user_repo.save(user)
        return RegisterResult(id=saved.id, email=saved.email, name=saved.name)
