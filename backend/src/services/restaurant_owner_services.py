from src.repositories.user_repo import UserRepo
from src.models.user_model import UserInternal
from src.schemas.user_schema import UserRole


class RestaurantOwnerService:
    @staticmethod
    def _role_value(user_data: dict) -> str | None:
        role = user_data.get("role")
        if isinstance(role, UserRole):
            return role.value
        return role

    @staticmethod
    async def assign_user_as_staff(owner_username: str, staff_username: str) -> dict:
        owner = await UserRepo.get_by_username(owner_username)
        if not owner:
            raise ValueError("Owner not found")

        if RestaurantOwnerService._role_value(owner) != UserRole.RESTAURANT_OWNER.value:
            raise ValueError("User is not a restaurant owner")

        owner_restaurant_id = owner.get("restaurant_id")
        if not owner_restaurant_id:
            raise ValueError("Owner has no associated restaurant")

        target_user = await UserRepo.get_by_username(staff_username)
        if not target_user:
            raise ValueError("User not found")

        if (
            RestaurantOwnerService._role_value(target_user)
            == UserRole.RESTAURANT_OWNER.value
        ):
            raise ValueError("Cannot assign restaurant owner as staff")

        if (
            RestaurantOwnerService._role_value(target_user)
            == UserRole.RESTAURANT_STAFF.value
        ):
            return UserInternal.model_validate(target_user)

        updated_user = await UserRepo.update_by_username(
            staff_username,
            {
                "role": UserRole.RESTAURANT_STAFF,
                "restaurant_id": owner_restaurant_id,
                "requires_2fa": True,
            },
        )
        if not updated_user:
            raise ValueError("User not found")

        return UserInternal.model_validate(updated_user)
