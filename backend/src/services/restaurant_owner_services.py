from src.repositories.user_repo import UserRepo
from src.repositories.restaurant_repo import RestaurantRepo
from src.repositories.order_repo import OrderRepo
from src.models.user_model import UserInternal
from src.schemas.user_schema import UserRole
from src.core.utils import get_role_value
from src.services.order_services import OrderService

class RestaurantOwnerService:

    @staticmethod
    async def assign_user_as_staff(owner_username: str, staff_username: str) -> dict:
        owner = await UserRepo.get_by_username(owner_username)
        if not owner:
            raise ValueError('Owner not found')
        if get_role_value(owner) != UserRole.RESTAURANT_OWNER.value:
            raise ValueError('User is not a restaurant owner')
        owner_restaurant_id = owner.get('restaurant_id')
        if not owner_restaurant_id:
            raise ValueError('Owner has no associated restaurant')
        target_user = await UserRepo.get_by_username(staff_username)
        if not target_user:
            raise ValueError('User not found')
        if get_role_value(target_user) == UserRole.RESTAURANT_OWNER.value:
            raise ValueError('Cannot assign restaurant owner as staff')
        if get_role_value(target_user) == UserRole.RESTAURANT_STAFF.value:
            return UserInternal.model_validate(target_user)
        updated_user = await UserRepo.update_by_username(staff_username, {'role': UserRole.RESTAURANT_STAFF, 'restaurant_id': owner_restaurant_id, 'requires_2fa': True})
        if not updated_user:
            raise ValueError('User not found')
        return UserInternal.model_validate(updated_user)

    @staticmethod
    async def _assert_staff_or_owner(restaurant_id: int, username: str) -> str:
        user = await UserRepo.get_by_username(username)
        if not user:
            raise ValueError('User not found')
        user_role = get_role_value(user)
        user_restaurant_id = user.get('restaurant_id')
        is_owner = user_role == UserRole.RESTAURANT_OWNER.value and user_restaurant_id == restaurant_id
        is_staff = user_role == UserRole.RESTAURANT_STAFF.value and user_restaurant_id == restaurant_id
        if not (is_owner or is_staff):
            raise ValueError("User does not have permission to view this restaurant's orders")
        restaurants = await RestaurantRepo.read_all()
        key = str(restaurant_id)
        if isinstance(restaurants, dict):
            if key not in restaurants:
                raise ValueError('Restaurant not found')
        elif isinstance(restaurants, list):
            found = any((isinstance(r, dict) and (r.get('restaurant_id') == restaurant_id or r.get('id') == restaurant_id)) for r in restaurants)
            if not found:
                raise ValueError('Restaurant not found')
        else:
            raise ValueError('Restaurant not found')
        return f'Restaurant_{restaurant_id}'

    @staticmethod
    def _append_paid_restaurant_order(order_data: dict, restaurant_key: str, bucket: list) -> None:
        if order_data.get('restaurant') != restaurant_key:
            return
        if order_data.get('payment_status') != 'accepted':
            return
        bucket.append(OrderService._dict_to_order(order_data))

    @staticmethod
    async def get_restaurant_orders(restaurant_id: int, username: str) -> list:
        restaurant_key = await RestaurantOwnerService._assert_staff_or_owner(restaurant_id, username)
        all_orders = await OrderRepo.get_all_orders()
        restaurant_orders = []
        for order_data in all_orders.values():
            RestaurantOwnerService._append_paid_restaurant_order(order_data, restaurant_key, restaurant_orders)
        return restaurant_orders

    @staticmethod
    async def get_restaurant_orders_by_status(restaurant_id: int, username: str, status: str) -> list:
        restaurant_key = await RestaurantOwnerService._assert_staff_or_owner(restaurant_id, username)
        orders_by_status = await OrderRepo.get_orders_by_status(status)
        restaurant_orders = []
        for order_data in orders_by_status:
            RestaurantOwnerService._append_paid_restaurant_order(order_data, restaurant_key, restaurant_orders)
        return restaurant_orders

    @staticmethod
    async def get_restaurant_orders_by_date_range(restaurant_id: int, username: str, start_time: int, end_time: int) -> list:
        restaurant_key = await RestaurantOwnerService._assert_staff_or_owner(restaurant_id, username)
        orders_by_date = await OrderRepo.get_orders_by_date_range(start_time, end_time)
        restaurant_orders = []
        for order_data in orders_by_date:
            RestaurantOwnerService._append_paid_restaurant_order(order_data, restaurant_key, restaurant_orders)
        return restaurant_orders

    @staticmethod
    async def get_restaurant_orders_by_status_and_date(restaurant_id: int, username: str, status: str, start_time: int, end_time: int) -> list:
        restaurant_key = await RestaurantOwnerService._assert_staff_or_owner(restaurant_id, username)
        orders_filtered = await OrderRepo.get_orders_by_status_and_date(status, start_time, end_time)
        restaurant_orders = []
        for order_data in orders_filtered:
            RestaurantOwnerService._append_paid_restaurant_order(order_data, restaurant_key, restaurant_orders)
        return restaurant_orders
