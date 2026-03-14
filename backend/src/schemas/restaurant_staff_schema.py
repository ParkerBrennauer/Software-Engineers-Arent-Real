from src.schemas.user_schema import UserBase, UserRegister, UserRole, UserUpdate


class RestaurantStaffBase(UserBase):
    role: UserRole = UserRole.RESTAURANT_STAFF
    restaurant_id: int


class RestaurantStaffRegister(RestaurantStaffBase, UserRegister):
    pass


class RestaurantStaffUpdate(UserUpdate):
    restaurant_id: int | None = None
