import json
from typing import List, Optional
import aiofiles

from src.core.config import USERS_FILE


class UserRepo:
    FILE_PATH = USERS_FILE

    @classmethod
    async def read_all(cls) -> List[dict]:

        if not cls.FILE_PATH.exists():
            return []

        async with aiofiles.open(cls.FILE_PATH, mode="r") as f:
            content = await f.read()
            if not content:
                return []

            data = json.loads(content)
            if isinstance(data, dict):
                return list(data.values())
            return data if isinstance(data, list) else []

    @classmethod
    async def save_user(cls, user_data: dict) -> dict:
        users = await cls.read_all()

        new_id = max((u.get("id", 0) for u in users), default=0) + 1
        user_data["id"] = new_id
        users.append(user_data)

        async with aiofiles.open(cls.FILE_PATH, mode="w") as f:
            await f.write(json.dumps(users, indent=4))

        return user_data

    @classmethod
    async def get_by_username(cls, username: str) -> Optional[dict]:
        users = await cls.read_all()

        for user in users:
            if user["username"] == username:
                return user
        return None

    @classmethod
    async def update_by_username(cls, username: str, updates: dict) -> Optional[dict]:
        users = await cls.read_all()

        for index, user in enumerate(users):
            if user["username"] == username:
                users[index].update(updates)

                async with aiofiles.open(cls.FILE_PATH, mode="w") as f:
                    await f.write(json.dumps(users, indent=4))

                return users[index]

        return None
