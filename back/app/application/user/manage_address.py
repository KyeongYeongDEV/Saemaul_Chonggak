from dataclasses import dataclass

from app.core.exceptions import ForbiddenError
from app.domain.user.entities import UserAddress
from app.domain.user.repository import UserAddressRepository


@dataclass
class CreateAddressCommand:
    user_id: int
    name: str
    receiver: str
    phone: str
    zipcode: str
    address1: str
    address2: str | None
    is_default: bool


class AddressUseCase:
    def __init__(self, address_repo: UserAddressRepository):
        self._repo = address_repo

    async def list(self, user_id: int) -> list[UserAddress]:
        return await self._repo.list_by_user(user_id)

    async def create(self, cmd: CreateAddressCommand) -> UserAddress:
        if cmd.is_default:
            await self._repo.clear_default(cmd.user_id)
        address = UserAddress(
            id=None, user_id=cmd.user_id, name=cmd.name, receiver=cmd.receiver,
            phone=cmd.phone, zipcode=cmd.zipcode, address1=cmd.address1,
            address2=cmd.address2, is_default=cmd.is_default,
        )
        return await self._repo.save(address)

    async def delete(self, user_id: int, address_id: int) -> None:
        address = await self._repo.get_by_id(address_id)
        if not address or address.user_id != user_id:
            raise ForbiddenError()
        await self._repo.delete(address_id)
