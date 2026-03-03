from src.schemas.user_schema import UserRegister, UserResponse, UserRole
from src.repositories.user_repo import get_by_username, save_user
from src.models.user_model import UserInternal
import json

class UserService:

  @staticmethod
  async def create_user(user_in: UserRegister) -> dict:
    
    existing_user = await get_by_username(user_in.username)
    if existing_user:
      raise ValueError("Username already exists")

    requires_2fa = user_in in [UserRole.DRIVER, UserRole.RESTAURANT_OWNER, UserRole.RESTAURANT_STAFF]
    
    user_data = user_in.model_dump()
    user_data["hashed_pasword"] = user_in.password #Change to hashed password
    user_data["requires_2fa"] = requires_2fa
    user_data["is_active"] = True
    
    del user_data["password"]
    saved_data = await save_user(user_data)
    
    return UserInternal.model_validate(saved_data)