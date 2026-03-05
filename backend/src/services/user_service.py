from src.schemas.user_schema import UserRegister, UserRole
from src.repositories.user_repo import UserRepo
from src.models.user_model import UserInternal
from passlib.context import CryptContext

# Use bcrypt for password salting and hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    async def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def create_user(user_in: UserRegister) -> dict:

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
