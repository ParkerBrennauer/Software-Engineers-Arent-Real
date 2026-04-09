from src.schemas.order_schema import OrderCreate, Order
from src.models.order_model import OrderInternal
from src.repositories.order_repo import OrderRepo
from src.repositories.user_repo import UserRepo
from src.repositories.restaurant_repo import RestaurantRepo
from src.utils.distance import calculate_distance

class OrderService:

    @staticmethod
    async def get_distance(customer: str, restaurant: str) -> float:
        try:
            users = await UserRepo.read_all()
            customer_data = next((u for u in users if u.get('username') == customer), None)
            if not customer_data or not customer_data.get('location') or (not customer_data['location']):
                return 0.0
            customer_lon, customer_lat = customer_data['location'][0]
            restaurant_id_str = restaurant.replace('Restaurant_', '')
            restaurants = await RestaurantRepo.read_all()
            if isinstance(restaurants, dict):
                restaurant_data = restaurants.get(restaurant_id_str)
            else:
                restaurant_data = next((r for r in restaurants if str(r.get('restaurant_id')) == restaurant_id_str), None)
            if not restaurant_data or not restaurant_data.get('location'):
                return 0.0
            restaurant_lon, restaurant_lat = restaurant_data['location']
            return calculate_distance(customer_lon, customer_lat, restaurant_lon, restaurant_lat)
        except Exception:
            return 0.0

    @staticmethod
    async def create_order(create_order: OrderCreate) -> dict:
        order_data = create_order.model_dump()
        order_data['order_status'] = 'payment pending'
        order_data['payment_status'] = 'pending'
        largest_order_id = await OrderRepo.get_largest_order_id()
        order_data['id'] = largest_order_id + 1 if largest_order_id is not None else 1
        order_data['locked'] = False
        order_data['items'] = order_data.get('items', [])
        if order_data.get('distance') is None:
            order_data['distance'] = await OrderService.get_distance(order_data.get('customer', ''), order_data.get('restaurant', ''))
        order_data['cost'] = await OrderService.calculate_order_cost(order_data['items'], order_data.get('distance', 0.0))
        saved_data = await OrderRepo.save_order(order_data)
        return OrderInternal.model_validate(saved_data)

    @staticmethod
    async def update_order(order_id: int, update_data: dict) -> OrderInternal:
        existing_order = await OrderRepo.get_order(order_id)
        if existing_order is None:
            raise ValueError('Order not found')
        if isinstance(existing_order, Order):
            existing_order = existing_order.model_dump()
        if existing_order.get('locked'):
            raise ValueError('Order is locked and cannot be updated')
        updated_order = {**existing_order, **update_data}
        updated_order['items'] = update_data.get('items', existing_order.get('items', []))
        updated_order['cost'] = await OrderService.calculate_order_cost(updated_order['items'], updated_order.get('distance', 0.0))
        saved_order = await OrderRepo.update_order(order_id, updated_order)
        if isinstance(saved_order, str):
            return saved_order
        if isinstance(saved_order, dict) and 'id' not in saved_order:
            saved_order['id'] = int(order_id)
        return OrderInternal.model_validate(saved_order)

    @staticmethod
    async def calculate_order_cost(items: list, distance: float=0.0) -> float:
        total = 0.0
        for item in items:
            if isinstance(item, dict):
                total += item.get('price', 0)
            else:
                total += 0
        delivery_fee = 2.0 + distance * 0.5
        total += delivery_fee
        total *= 1.13
        return round(total, 2)

    @staticmethod
    async def lock_order(order_id: int) -> OrderInternal:
        existing_order = await OrderRepo.get_order(order_id)
        if existing_order is None:
            raise ValueError('Order not found')
        if isinstance(existing_order, Order):
            existing_order = existing_order.model_dump()
        if existing_order.get('locked'):
            return OrderInternal.model_validate(existing_order)
        updated_order = {**existing_order, 'locked': True}
        saved_data = await OrderRepo.update_order(order_id, updated_order)
        if isinstance(saved_data, str):
            return saved_data
        if isinstance(saved_data, dict) and 'id' not in saved_data:
            saved_data['id'] = int(order_id)
        return OrderInternal.model_validate(saved_data)

    @staticmethod
    async def get_order_status(order_id: int):
        existing_order = await OrderRepo.get_order(order_id)
        if existing_order is None:
            raise ValueError('Order not found')
        return existing_order

    @staticmethod
    async def cancel_order(order_id: int):
        return await OrderService.update_order(order_id, {'order_status': 'cancelled'})

    @staticmethod
    async def mark_ready_for_pickup(order_id: int):
        return await OrderService.update_order(order_id, {'order_status': 'ready_for_pickup'})

    @staticmethod
    async def assign_driver(order_id: int, driver: str):
        return await OrderService.update_order(order_id, {'driver': driver})

    @staticmethod
    async def get_driver_orders(driver: str):
        return await OrderRepo.get_orders_by_driver(driver)

    @staticmethod
    async def pickup_order(order_id: int):
        return await OrderService.update_order(order_id, {'order_status': 'picked_up'})

    @staticmethod
    async def report_restaurant_delay(order_id: int, reason: str):
        updated = await OrderService.update_order(order_id, {'order_status': 'delayed', 'delay_reason': reason})
        if 'cancel' in reason.lower() or 'cannot prepare' in reason.lower():
            return await OrderService.process_refund(order_id)
        return updated

    @staticmethod
    async def report_driver_delay(order_id: int, reason: str):
        return await OrderService.update_order(order_id, {'order_status': 'delayed', 'delay_reason': reason})

    @staticmethod
    async def process_refund(order_id: int):
        order = await OrderRepo.get_order(order_id)
        if order is None:
            raise ValueError('Order not found')
        if isinstance(order, Order):
            order_dict = order.model_dump()
        else:
            order_dict = order
        if order_dict.get('refund_issued', False):
            raise ValueError('Refund already issued')
        if order_dict.get('order_status') not in ['delayed', 'cancelled']:
            raise ValueError('Refund not applicable')
        if order_dict.get('payment_status') != 'accepted':
            raise ValueError('Cannot refund unpaid order')
        updated_order = {**order_dict, 'id': order_dict.get('id', int(order_id)), 'refund_issued': True, 'refund_amount': order_dict.get('cost', 0)}
        saved = await OrderRepo.update_order(order_id, updated_order)
        if isinstance(saved, str):
            return saved
        if isinstance(saved, Order):
            saved = saved.model_dump()
        if isinstance(saved, dict) and 'id' not in saved:
            saved['id'] = int(order_id)
        return OrderInternal.model_validate(saved)

    @staticmethod
    async def get_restaurant_orders(restaurant: str):
        orders = await OrderRepo.get_all_orders()
        result = []
        for order_data in orders.values():
            if order_data.get('restaurant') == restaurant:
                result.append(Order(**order_data))
        return result

    @staticmethod
    async def get_previous_orders_by_user(username: str):
        orders = await OrderRepo._read_raw()
        results = []
        if not username:
            raise ValueError('No username submitted')
        for order_id, order in orders.items():
            if order['customer'] == username:
                hydrated_order = dict(order)
                hydrated_order.setdefault('id', str(order_id))
                results.append(hydrated_order)
        return results
