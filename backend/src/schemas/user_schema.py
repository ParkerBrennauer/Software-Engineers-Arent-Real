from pydantic import BaseModel, EmailStr
from src.schemas.user_schema_abstract import (
    UserBaseAbstract,
    UserResponseAbstract,
    UserRole,
    UserUpdateAbstract
)


class UserBase(UserBaseAbstract, BaseModel):
    email: EmailStr
    name: str
    role: UserRole
    username: str


class UserRegister(UserBase):
    password: str


class UserUpdate(UserUpdateAbstract, BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    role: UserRole | None = None
    username: str | None = None
    password: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserResponseAbstract, BaseModel):
    id: int
    requires_2fa: bool = False
