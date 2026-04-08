from src.schemas.user_schema import UserRole

def get_role_value(user_data: dict) -> str | None:
    role = user_data.get('role')
    if isinstance(role, UserRole):
        return role.value
    return role
