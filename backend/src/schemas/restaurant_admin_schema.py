from src.schemas.user_schema import UserRegister, UserUpdate, UserRole


class RestaurantOwnerRegister(UserRegister):
    role: UserRole = UserRole.RESTAURANT_OWNER


class RestaurantStaffRegister(UserRegister):
    role: UserRole = UserRole.RESTAURANT_STAFF


class RestaurantAdminUpdate(UserUpdate):
    pass
