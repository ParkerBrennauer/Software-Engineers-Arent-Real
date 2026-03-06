from __future__ import annotations

from abc import ABC, abstractmethod

from src.models.user_model import UserInternal
from src.schemas.user_schema import UserRegister, UserUpdate


class UserServiceAbstract(ABC):
    @staticmethod
    @abstractmethod
    async def get_password_hash(password: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        pass

    @staticmethod
    @abstractmethod
    async def create_user(user_in: UserRegister) -> UserInternal:
        pass

    @staticmethod
    @abstractmethod
    async def update_user(username: str, user_in: UserUpdate) -> UserInternal:
        pass
