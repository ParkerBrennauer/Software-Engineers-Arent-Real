from src.schemas.user_schema import UserRegister, UserRole, UserUpdate
from src.repositories.user_repo import UserRepo
from src.models.user_model import UserInternal
from src.services.user_service_abstract import UserServiceAbstract
from passlib.context import CryptContext

# Use bcrypt for password salting and hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(UserServiceAbstract):
    @staticmethod
    async def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def create_user(user_in: UserRegister) -> UserInternal:

        existing_user = await UserRepo.get_by_username(user_in.username)
        if existing_user:
            raise ValueError("Username already exists")

        requires_2fa = user_in.role in [
            UserRole.DRIVER, UserRole.RESTAURANT_OWNER, UserRole.RESTAURANT_STAFF]

        user_data = user_in.model_dump()
        user_data["hashed_password"] = await UserService.get_password_hash(user_in.password)
        user_data["requires_2fa"] = requires_2fa
        user_data["is_active"] = True
        del user_data["password"]

        saved_data = await UserRepo.save_user(user_data)

        return UserInternal.model_validate(saved_data)

    @staticmethod
    async def update_user(username: str, user_in: UserUpdate) -> UserInternal:
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
            update_data["hashed_password"] = \
                await UserService.get_password_hash(update_data["password"])
            del update_data["password"]

        if "role" in update_data:
            update_data["requires_2fa"] = update_data["role"] in [
                UserRole.DRIVER, UserRole.RESTAURANT_OWNER, UserRole.RESTAURANT_STAFF
            ]

        updated_user = await UserRepo.update_by_username(username, update_data)
        if not updated_user:
            raise ValueError("User not found")

        return UserInternal.model_validate(updated_user)
