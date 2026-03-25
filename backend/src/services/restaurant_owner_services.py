from src.repositories.user_repo import UserRepo
from src.repositories.restaurant_repo import RestaurantRepo
from src.repositories.order_repo import OrderRepo
from src.models.user_model import UserInternal
from src.schemas.user_schema import UserRole
from src.schemas.order_schema import Order


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

    @staticmethod
    async def get_restaurant_orders(restaurant_id: int, username: str) -> list:
        user = await UserRepo.get_by_username(username)
        if not user:
            raise ValueError("User not found")

        user_role = RestaurantOwnerService._role_value(user)
        user_restaurant_id = user.get("restaurant_id")

        is_owner = (
            user_role == UserRole.RESTAURANT_OWNER.value
            and user_restaurant_id == restaurant_id
        )
        is_staff = (
            user_role == UserRole.RESTAURANT_STAFF.value
            and user_restaurant_id == restaurant_id
        )

        if not (is_owner or is_staff):
            raise ValueError(
                "User does not have permission to view this restaurant's orders"
            )

        restaurants = await RestaurantRepo.read_all()
        restaurant_name = None
        for restaurant in restaurants:
            if restaurant.get("id") == restaurant_id:
                restaurant_name = restaurant.get("name")
                break

        if not restaurant_name:
            raise ValueError("Restaurant not found")

        all_orders = await OrderRepo.get_all_orders()
        restaurant_orders = []

        for order_data in all_orders.values():
            if order_data.get("restaurant") == restaurant_name:
                restaurant_orders.append(Order(**order_data))

        return restaurant_orders
