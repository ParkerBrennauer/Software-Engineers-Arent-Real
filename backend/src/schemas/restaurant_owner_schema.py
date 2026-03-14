from pydantic import BaseModel

from src.schemas.user_schema import UserBase, UserRegister, UserRole, UserUpdate


class RestaurantOwnerBase(UserBase):
    role: UserRole = UserRole.RESTAURANT_OWNER
    restaurant_id: int


class RestaurantOwnerRegister(RestaurantOwnerBase, UserRegister):
    pass


class RestaurantOwnerUpdate(UserUpdate):
    restaurant_id: int | None = None


class RestaurantOwnerAssignStaffRequest(BaseModel):
    staff_username: str
