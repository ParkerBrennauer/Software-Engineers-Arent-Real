import os
import json
from typing import List, Optional
import aiofiles


class UserRepo:
    FILE_PATH = "../data/users.json"

    @classmethod
    async def read_all(cls) -> List[dict]:

        if not os.path.exists(cls.FILE_PATH):
            return {}

        async with aiofiles.open(cls.FILE_PATH, mode='r') as f:
            users = await f.read()
            return json.loads(users) if users else {}

    @classmethod
    async def save_user(cls, user_data: dict) -> dict:
        users = await cls.read_all()

        if not isinstance(users, dict):
            users = {}

        new_id = max((int(user_id) for user_id in users.keys()), default=0) + 1
        user_data["id"] = new_id

        users[str(new_id)] = user_data

        async with aiofiles.open(cls.FILE_PATH, mode='w') as f:
            await f.write(json.dumps(users, indent=4))

        return user_data

    @classmethod
    async def get_by_username(cls, username: str) -> Optional[dict]:
        users = await cls.read_all()

        for user in users.values():
            if user["username"] == username:
                return user
        return None

    @classmethod
    async def update_by_username(cls, username: str, updates: dict) -> Optional[dict]:
        users = await cls.read_all()

        for index, user in enumerate(users):
            if user["username"] == username:
                users[index].update(updates)

                async with aiofiles.open(cls.FILE_PATH, mode='w') as f:
                    await f.write(json.dumps(users, indent=4))

                return users[index]

        return None
