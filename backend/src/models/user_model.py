from typing import Optional
from src.schemas.user_schema import UserBase


class UserInternal(UserBase):
    id: int
    hashed_password: str
    is_active: bool = True
    two_factor_code: Optional[str] = None
    two_factor_expires_at: Optional[str] = None
