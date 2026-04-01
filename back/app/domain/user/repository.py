from abc import ABC, abstractmethod

from app.domain.user.entities import User, UserAddress


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...


class UserAddressRepository(ABC):
    @abstractmethod
    async def get_by_id(self, address_id: int) -> UserAddress | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[UserAddress]: ...

    @abstractmethod
    async def save(self, address: UserAddress) -> UserAddress: ...

    @abstractmethod
    async def delete(self, address_id: int) -> None: ...

    @abstractmethod
    async def clear_default(self, user_id: int) -> None: ...
