from src.schemas.user_schema import UserBase


class UserInternal(UserBase):
    id: int
    hashed_password: str
    is_active: bool = True
