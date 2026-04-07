import random

from src.repositories.order_repo import OrderRepo
from src.schemas.order_schema import OrderStatus
from src.schemas.order_tracking_schema import (
    OrderTrackingResponse,
    OrderTrackingStatusUpdate,
)


class OrderTrackingService:
    RESTAURANT_STATUSES = {
        OrderStatus.CREATED,
        OrderStatus.PAYMENT_PENDING,
        OrderStatus.PAYMENT_ACCEPTED,
        OrderStatus.CONFIRMED,
        OrderStatus.PREPARING,
        OrderStatus.READY_FOR_PICKUP,
    }
    DELIVERY_STATUSES = {
        OrderStatus.PICKED_UP,
        OrderStatus.OUT_FOR_DELIVERY,
        OrderStatus.DELAYED,
    }
    INACTIVE_TRACKING_STATUSES = {
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED,
        OrderStatus.PAYMENT_REJECTED,
    }

    @staticmethod
    def _coerce_status(status: str | OrderStatus | None) -> OrderStatus:
        if isinstance(status, OrderStatus):
            return status

        if not status:
            return OrderStatus.PAYMENT_PENDING

        try:
            return OrderStatus(status)
        except ValueError:
            return OrderStatus.PAYMENT_PENDING

    @staticmethod
    def _coerce_distance(distance: float | int | None) -> float:
        if distance is None:
            return 0.0

        return round(float(distance), 2)

    @staticmethod
    def _coerce_time(time_minutes: int | float | None) -> int:
        if time_minutes is None:
            return 0

        return max(0, int(time_minutes))

    @staticmethod
    def _generate_distance(minimum: float = 1.0, maximum: float = 15.0) -> float:
        return round(random.uniform(minimum, maximum), 2)

    @staticmethod
    def _generate_time(minimum: int = 8, maximum: int = 50) -> int:
        return random.randint(minimum, maximum)

    @classmethod
    def _ensure_restaurant_metrics(
        cls, distance: float, time_minutes: int
    ) -> tuple[float, int]:
        if distance <= 0:
            distance = cls._generate_distance()
        if time_minutes <= 0:
            time_minutes = cls._generate_time()
        return distance, time_minutes

    @classmethod
    def _resolve_delivery_tracking(
        cls, status: OrderStatus, distance: float, time_minutes: int, refresh: bool
    ) -> tuple[OrderStatus, float, int]:
        if distance <= 0:
            distance = cls._generate_distance(0.5, 10.0)
        if time_minutes <= 0:
            time_minutes = cls._generate_time(5, 35)

        if not refresh:
            return status, distance, time_minutes

        distance = round(max(0.0, distance - random.uniform(0.3, 2.5)), 2)
        time_minutes = max(0, time_minutes - random.randint(2, 8))

        if distance == 0.0 or time_minutes == 0:
            return OrderStatus.DELIVERED, 0.0, 0

        return status, distance, time_minutes

    @classmethod
    def _resolve_tracking_progress(
        cls, status: OrderStatus, distance: float, time_minutes: int, refresh: bool
    ) -> tuple[OrderStatus, float, int]:
        if status in cls.INACTIVE_TRACKING_STATUSES:
            return status, 0.0, 0

        if status in cls.RESTAURANT_STATUSES:
            distance, time_minutes = cls._ensure_restaurant_metrics(
                distance,
                time_minutes,
            )
            return status, distance, time_minutes

        if status in cls.DELIVERY_STATUSES:
            delivery_status, distance, time_minutes = cls._resolve_delivery_tracking(
                status,
                distance,
                time_minutes,
                refresh,
            )
            return delivery_status, distance, time_minutes

        return status, distance, time_minutes

    @classmethod
    def _build_tracking_updates(
        cls, order: dict, status: OrderStatus, distance: float, time_minutes: int
    ) -> dict[str, object]:
        updates: dict[str, object] = {}

        if cls._coerce_status(order.get("order_status")) != status:
            updates["order_status"] = status.value
        if cls._coerce_distance(order.get("distance")) != distance:
            updates["distance"] = distance
        if cls._coerce_time(order.get("time")) != time_minutes:
            updates["time"] = time_minutes

        return updates

    @classmethod
    async def get_tracking_info(cls, order_id: str) -> OrderTrackingResponse:
        order = await OrderRepo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        tracked_order = await cls._sync_tracking_state(order_id, order, refresh=False)
        return cls._build_tracking_response(order_id, tracked_order)

    @classmethod
    async def refresh_tracking(cls, order_id: str) -> OrderTrackingResponse:
        order = await OrderRepo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        tracked_order = await cls._sync_tracking_state(order_id, order, refresh=True)
        return cls._build_tracking_response(order_id, tracked_order)

    @classmethod
    async def update_tracking_status(
        cls, order_id: str, tracking_update: OrderTrackingStatusUpdate
    ) -> OrderTrackingResponse:
        order = await OrderRepo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        saved_order = await OrderRepo.update_order(
            order_id,
            {
                "order_status": tracking_update.order_status.value,
                "driver": tracking_update.driver
                if tracking_update.driver is not None
                else order.get("driver"),
            },
        )
        if not saved_order:
            raise ValueError("Order not found")

        tracked_order = await cls._sync_tracking_state(
            order_id, saved_order, refresh=True
        )
        return cls._build_tracking_response(order_id, tracked_order)

    @classmethod
    async def _sync_tracking_state(
        cls, order_id: str, order: dict, refresh: bool
    ) -> dict:
        status = cls._coerce_status(order.get("order_status"))
        distance = cls._coerce_distance(order.get("distance"))
        time_minutes = cls._coerce_time(order.get("time"))
        status, distance, time_minutes = cls._resolve_tracking_progress(
            status,
            distance,
            time_minutes,
            refresh,
        )
        updates = cls._build_tracking_updates(order, status, distance, time_minutes)

        if not updates:
            normalized_order = dict(order)
            normalized_order["order_status"] = status.value
            normalized_order["distance"] = distance
            normalized_order["time"] = time_minutes
            return normalized_order

        saved_order = await OrderRepo.update_order(order_id, updates)
        if not saved_order:
            raise ValueError("Order not found")

        return saved_order

    @classmethod
    def _build_tracking_response(
        cls, order_id: str, order: dict
    ) -> OrderTrackingResponse:
        status = cls._coerce_status(order.get("order_status"))

        if status == OrderStatus.DELIVERED:
            current_location = "delivered"
            status_message = "Your order has been delivered."
        elif status == OrderStatus.CANCELLED:
            current_location = "cancelled"
            status_message = "Your order has been cancelled."
        elif status == OrderStatus.PAYMENT_REJECTED:
            current_location = "payment rejected"
            status_message = "Payment was rejected for this order."
        elif status in cls.RESTAURANT_STATUSES:
            current_location = "at restaurant"
            status_message = "Your order is still being prepared at the restaurant."
        elif status in cls.DELIVERY_STATUSES:
            current_location = "with driver"
            status_message = "Your order is on the way to the drop-off location."
        else:
            current_location = "order created"
            status_message = "Your order is being processed."

        return OrderTrackingResponse(
            order_id=str(order_id),
            restaurant=order.get("restaurant", ""),
            customer=order.get("customer", ""),
            driver=order.get("driver"),
            order_status=status,
            delivery_instructions=order.get("delivery_instructions"),
            current_location=current_location,
            distance_km=cls._coerce_distance(order.get("distance")),
            estimated_time_minutes=cls._coerce_time(order.get("time")),
            status_message=status_message,
        )
