from app.core.exceptions import UserNotFoundError
from app.domain.user.entities import User
from app.domain.user.repository import UserRepository


class GetProfileUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, user_id: int) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user
