from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.user.get_profile import GetProfileUseCase
from app.application.user.manage_address import AddressUseCase, CreateAddressCommand
from app.application.user.update_profile import UpdateProfileCommand, UpdateProfileUseCase
from app.core.dependencies import get_current_user_id
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.user_repo import SQLUserAddressRepository, SQLUserRepository
from app.presentation.schemas.common import ApiResponse
from app.presentation.schemas.user import (
    AddressRequest,
    AddressResponse,
    UpdateProfileRequest,
    UserProfileResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ApiResponse[UserProfileResponse])
async def get_me(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = await GetProfileUseCase(SQLUserRepository(db)).execute(user_id)
    return ApiResponse(data=UserProfileResponse(
        id=user.id, email=user.email, name=user.name, phone=user.phone, role=user.role.value, point=user.point
    ))


@router.patch("/me", response_model=ApiResponse[UserProfileResponse])
async def update_me(
    body: UpdateProfileRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await UpdateProfileUseCase(SQLUserRepository(db)).execute(
        UpdateProfileCommand(user_id=user_id, name=body.name, phone=body.phone)
    )
    return ApiResponse(data=UserProfileResponse(
        id=user.id, email=user.email, name=user.name, phone=user.phone, role=user.role.value, point=user.point
    ))


@router.get("/me/addresses", response_model=ApiResponse[list[AddressResponse]])
async def list_addresses(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    addresses = await AddressUseCase(SQLUserAddressRepository(db)).list(user_id)
    return ApiResponse(data=[
        AddressResponse(id=a.id, name=a.name, receiver=a.receiver, phone=a.phone,
                        zipcode=a.zipcode, address1=a.address1, address2=a.address2, is_default=a.is_default)
        for a in addresses
    ])


@router.post("/me/addresses", response_model=ApiResponse[AddressResponse], status_code=201)
async def create_address(
    body: AddressRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    address = await AddressUseCase(SQLUserAddressRepository(db)).create(
        CreateAddressCommand(
            user_id=user_id, name=body.name, receiver=body.receiver, phone=body.phone,
            zipcode=body.zipcode, address1=body.address1, address2=body.address2, is_default=body.is_default,
        )
    )
    return ApiResponse(data=AddressResponse(
        id=address.id, name=address.name, receiver=address.receiver, phone=address.phone,
        zipcode=address.zipcode, address1=address.address1, address2=address.address2, is_default=address.is_default,
    ))


@router.delete("/me/addresses/{address_id}", status_code=204)
async def delete_address(
    address_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await AddressUseCase(SQLUserAddressRepository(db)).delete(user_id, address_id)
