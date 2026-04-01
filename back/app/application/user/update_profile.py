from dataclasses import dataclass

from app.core.exceptions import UserNotFoundError
from app.domain.user.entities import User
from app.domain.user.repository import UserRepository


@dataclass
class UpdateProfileCommand:
    user_id: int
    name: str
    phone: str | None


class UpdateProfileUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, cmd: UpdateProfileCommand) -> User:
        user = await self._user_repo.get_by_id(cmd.user_id)
        if not user:
            raise UserNotFoundError()
        user.name = cmd.name
        user.phone = cmd.phone
        return await self._user_repo.update(user)
