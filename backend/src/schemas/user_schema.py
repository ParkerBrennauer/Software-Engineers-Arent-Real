from enum import Enum
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    CUSTOMER = "customer"
    DRIVER = "driver"
    RESTAURANT_OWNER = "owner"
    RESTAURANT_STAFF = "staff"


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole
    username: str


class UserRegister(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    role: UserRole | None = None
    username: str | None = None
    password: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class TwoFactorVerify(BaseModel):
    code: str


class TwoFactorResponse(BaseModel):
    message: str
    requires_2fa: bool = False


class UserResponse(BaseModel):
    id: int
    requires_2fa: bool = False
