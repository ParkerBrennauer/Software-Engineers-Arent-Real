import json
from typing import List, Optional
import os
import aiofiles


class UserRepo:
    FILE_PATH = "../data/users.json"

    @classmethod
    async def read_all(cls) -> List[dict]:

        if not os.path.exists(cls.FILE_PATH):
            return []

        async with aiofiles.open(cls.FILE_PATH, mode='r') as f:
            users = await f.read()
            return json.loads(users) if users else []

    @classmethod
    async def save_user(cls, user_data: dict) -> dict:
        users = await cls.read_all()

        new_id = max((u.get("id", 0) for u in users), default=0) + 1
        user_data["id"] = new_id
        users.append(user_data)

        async with aiofiles.open(cls.FILE_PATH, mode='w') as f:
            await f.write(json.dumps(users, indent=4))

        return user_data

    @classmethod
    async def get_by_username(cls, username: str) -> Optional[dict]:
        users = await cls.read_all()

        for user in users:
            if user["username"] == username:
                return user
        return None
