from __future__ import annotations

from abc import ABC, abstractmethod

from src.models.user_model import UserInternal
from src.schemas.user_schema import UserRegister, UserUpdate


class UserServiceAbstract(ABC):
    @staticmethod
    @abstractmethod
    async def create_user(user_in: UserRegister) -> UserInternal:
        pass

    @staticmethod
    @abstractmethod
    async def update_user(username: str, user_in: UserUpdate) -> UserInternal:
        pass
