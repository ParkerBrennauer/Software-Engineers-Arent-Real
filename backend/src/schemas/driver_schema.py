from src.schemas.user_schema import UserRegister, UserUpdate, UserRole


class DriverRegister(UserRegister):
    role: UserRole = UserRole.DRIVER


class DriverUpdate(UserUpdate):
    pass
