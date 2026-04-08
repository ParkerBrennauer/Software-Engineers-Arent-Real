import random
from datetime import datetime, timedelta, timezone
from src.schemas.user_schema import UserRegister, UserRole, UserUpdate
from src.repositories.user_repo import UserRepo
from src.repositories.item_repo import ItemRepo
from src.models.user_model import UserInternal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    async def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def login_user(username: str, password: str) -> dict:
        user = await UserRepo.get_by_username(username)
        if not user:
            raise ValueError("Invalid username or password")

        if not await UserService.verify_password(
            password, user.get("hashed_password", "")
        ):
            raise ValueError("Invalid username or password")

        if not user.get("is_active"):
            raise ValueError("User account is inactive")

        return UserInternal.model_validate(user)

    @staticmethod
    async def create_user(user_in: UserRegister) -> dict:

        existing_user = await UserRepo.get_by_username(user_in.username)
        if existing_user:
            raise ValueError("Username already exists")

        requires_2fa = user_in.role in [
            UserRole.DRIVER,
            UserRole.RESTAURANT_OWNER,
            UserRole.RESTAURANT_STAFF,
        ]

        user_data = user_in.model_dump()
        user_data["hashed_password"] = await UserService.get_password_hash(
            user_in.password
        )
        user_data["requires_2fa"] = requires_2fa
        user_data["is_active"] = True
        del user_data["password"]

        saved_data = await UserRepo.save_user(user_data)

        return UserInternal.model_validate(saved_data)

    @staticmethod
    async def update_user(username: str, user_in: UserUpdate) -> dict:
        existing_user = await UserRepo.get_by_username(username)
        if not existing_user:
            raise ValueError("User not found")

        update_data = user_in.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return UserInternal.model_validate(existing_user)

        new_username = update_data.get("username")
        if new_username and new_username != username:
            username_taken = await UserRepo.get_by_username(new_username)
            if username_taken:
                raise ValueError("Username already exists")

        if "password" in update_data:
            update_data["hashed_password"] = await UserService.get_password_hash(
                update_data["password"]
            )
            del update_data["password"]

        if "role" in update_data:
            update_data["requires_2fa"] = update_data["role"] in [
                UserRole.DRIVER,
                UserRole.RESTAURANT_OWNER,
                UserRole.RESTAURANT_STAFF,
            ]

        updated_user = await UserRepo.update_by_username(username, update_data)
        if not updated_user:
            raise ValueError("User not found")

        return UserInternal.model_validate(updated_user)

    @staticmethod
    async def reset_password(username: str, code: str, new_password: str) -> bool:
        await UserService.verify_2fa_code(username, code)

        hashed = await UserService.get_password_hash(new_password)
        updated = await UserRepo.update_by_username(
            username, {"hashed_password": hashed}
        )
        if not updated:
            raise ValueError("User not found")

        return True

    @staticmethod
    async def generate_2fa_code(username: str) -> str:
        user = await UserRepo.get_by_username(username)
        if not user:
            raise ValueError("User not found")

        code = f"{random.randint(0, 999999):06d}"
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

        await UserRepo.update_by_username(
            username,
            {
                "two_factor_code": code,
                "two_factor_expires_at": expires_at,
            },
        )

        return code

    @staticmethod
    async def verify_2fa_code(username: str, code: str) -> bool:
        user = await UserRepo.get_by_username(username)
        if not user:
            raise ValueError("User not found")

        stored_code = user.get("two_factor_code")
        expires_at = user.get("two_factor_expires_at")

        if not stored_code or not expires_at:
            raise ValueError("No 2FA code has been generated")

        if datetime.now(timezone.utc) > datetime.fromisoformat(expires_at):
            await UserRepo.update_by_username(
                username,
                {
                    "two_factor_code": None,
                    "two_factor_expires_at": None,
                },
            )
            raise ValueError("2FA code has expired")

        if code != stored_code:
            raise ValueError("Invalid 2FA code")

        await UserRepo.update_by_username(
            username,
            {
                "two_factor_code": None,
                "two_factor_expires_at": None,
            },
        )

        return True

    @staticmethod
    async def toggle_favourite(username: str, itemKey: str) -> str:
        """
        Toggle a user's favourite item while enforcing one favourite per restaurant.
        """
        # Input validation to prevent lookups with invalid values.
        if not isinstance(username, str) or not username.strip():
            raise ValueError("username must be a non-empty string")
        if not isinstance(itemKey, str) or not itemKey.strip():
            raise ValueError("itemKey must be a non-empty string")

        user = await UserRepo.get_by_username(username)
        if not user:
            raise ValueError("User not found")

        item = await ItemRepo.get_by_key(itemKey)
        if not item:
            raise ValueError("Item not found")

        restaurant_id = item.get("restaurant_id")
        if restaurant_id is None:
            raise ValueError("Item missing restaurant_id")

        favorites_raw = user.get("favourites", [])
        if not isinstance(favorites_raw, list):
            raise ValueError("User favourites must be a list")
        favourites = list(favorites_raw)

        # Toggle off if this exact item is already favourited.
        if itemKey in favourites:
            updated = [fav for fav in favourites if fav != itemKey]
            await UserRepo.update_by_username(username, {"favourites": updated})
            return "removed"

        # Enforce one favourite per restaurant by replacing any same-restaurant item.
        replaced = False
        updated_favourites: list[str] = []
        for favourite_key in favourites:
            favourite_item = await ItemRepo.get_by_key(favourite_key)
            favourite_restaurant_id = (
                favourite_item.get("restaurant_id")
                if isinstance(favourite_item, dict)
                else None
            )
            if favourite_restaurant_id == restaurant_id:
                replaced = True
                continue
            updated_favourites.append(favourite_key)

        updated_favourites.append(itemKey)
        await UserRepo.update_by_username(username, {"favourites": updated_favourites})
        return "replaced" if replaced else "added"
