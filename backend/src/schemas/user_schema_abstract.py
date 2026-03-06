from enum import Enum

from pydantic import EmailStr


class UserRole(str, Enum):
    CUSTOMER = "customer"
    DRIVER = "driver"
    RESTAURANT_OWNER = "owner"
    RESTAURANT_STAFF = "staff"


class UserBaseAbstract:
    email: EmailStr
    name: str
    role: UserRole
    username: str


class UserUpdateAbstract:
    email: EmailStr | None
    name: str | None
    role: UserRole | None
    username: str | None
    password: str | None


class UserResponseAbstract:
    id: int
    requires_2fa: bool
