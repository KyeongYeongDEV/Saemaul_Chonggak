from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.entities import User, UserAddress, UserRole
from app.domain.user.repository import UserAddressRepository, UserRepository
from app.infrastructure.persistence.models import UserAddressModel, UserModel


def _to_user(m: UserModel) -> User:
    return User(
        id=m.id,
        email=m.email,
        password=m.password,
        name=m.name,
        phone=m.phone,
        role=UserRole(m.role),
        is_active=m.is_active,
        point=m.point,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _to_address(m: UserAddressModel) -> UserAddress:
    return UserAddress(
        id=m.id,
        user_id=m.user_id,
        name=m.name,
        receiver=m.receiver,
        phone=m.phone,
        zipcode=m.zipcode,
        address1=m.address1,
        address2=m.address2,
        is_default=m.is_default,
    )


class SQLUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._s.get(UserModel, user_id)
        return _to_user(result) if result else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._s.execute(select(UserModel).where(UserModel.email == email))
        m = result.scalar_one_or_none()
        return _to_user(m) if m else None

    async def save(self, user: User) -> User:
        m = UserModel(
            email=user.email,
            password=user.password,
            name=user.name,
            phone=user.phone,
            role=user.role.value,
            is_active=user.is_active,
            point=user.point,
        )
        self._s.add(m)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_user(m)

    async def update(self, user: User) -> User:
        await self._s.execute(
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                name=user.name,
                phone=user.phone,
                is_active=user.is_active,
                point=user.point,
            )
        )
        return user

    async def list_paginated(self, page: int, size: int) -> tuple[list[User], int]:
        q = (
            select(UserModel)
            .order_by(UserModel.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        count_q = select(func.count()).select_from(UserModel)
        result = await self._s.execute(q)
        total = await self._s.scalar(count_q)
        return [_to_user(m) for m in result.scalars()], total or 0


class SQLUserAddressRepository(UserAddressRepository):
    def __init__(self, session: AsyncSession):
        self._s = session

    async def get_by_id(self, address_id: int) -> UserAddress | None:
        result = await self._s.get(UserAddressModel, address_id)
        return _to_address(result) if result else None

    async def list_by_user(self, user_id: int) -> list[UserAddress]:
        result = await self._s.execute(
            select(UserAddressModel).where(UserAddressModel.user_id == user_id)
        )
        return [_to_address(m) for m in result.scalars()]

    async def save(self, address: UserAddress) -> UserAddress:
        m = UserAddressModel(
            user_id=address.user_id,
            name=address.name,
            receiver=address.receiver,
            phone=address.phone,
            zipcode=address.zipcode,
            address1=address.address1,
            address2=address.address2,
            is_default=address.is_default,
        )
        self._s.add(m)
        await self._s.flush()
        await self._s.refresh(m)
        return _to_address(m)

    async def delete(self, address_id: int) -> None:
        m = await self._s.get(UserAddressModel, address_id)
        if m:
            await self._s.delete(m)

    async def clear_default(self, user_id: int) -> None:
        await self._s.execute(
            update(UserAddressModel)
            .where(UserAddressModel.user_id == user_id)
            .values(is_default=False)
        )
