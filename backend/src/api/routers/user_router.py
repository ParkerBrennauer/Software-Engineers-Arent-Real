from fastapi import APIRouter, HTTPException, status
from src.schemas.user_schema import UserBase, UserRegister, UserLogin, UserRole, UserResponse
from src.services.user_service import UserService
#Define the prefix for the endpoints
router = APIRouter(prefix="/users", tags=["users"])

#Input must follow the UserRegister model
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegister):
  new_user = await UserService.create_user(user_in)
  return new_user