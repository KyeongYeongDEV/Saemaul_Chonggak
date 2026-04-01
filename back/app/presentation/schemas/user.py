from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: str | None
    role: str
    point: int


class UpdateProfileRequest(BaseModel):
    name: str
    phone: str | None = None


class AddressRequest(BaseModel):
    name: str
    receiver: str
    phone: str
    zipcode: str
    address1: str
    address2: str | None = None
    is_default: bool = False


class AddressResponse(BaseModel):
    id: int
    name: str
    receiver: str
    phone: str
    zipcode: str
    address1: str
    address2: str | None
    is_default: bool
