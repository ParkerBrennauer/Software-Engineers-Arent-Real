import pytest

from src.repositories.order_repo import OrderRepo
from src.schemas.order_schema import OrderStatus
from src.schemas.order_tracking_schema import OrderTrackingStatusUpdate
from src.services.order_tracking_service import OrderTrackingService
import src.services.order_tracking_service as order_tracking_service_module


@pytest.mark.asyncio
async def test_get_tracking_info_generates_metrics_for_restaurant_stage(monkeypatch):
    order = {
        "restaurant": "Restaurant_16",
        "customer": "customer_1",
        "driver": None,
        "order_status": OrderStatus.PREPARING.value,
        "distance": 0.0,
        "time": 0,
    }
    saved_updates = {}

    async def fake_get_by_id(_order_id: str):
        return dict(order)

    async def fake_update_order(order_id: str, updates: dict):
        saved_updates["order_id"] = order_id
        saved_updates["updates"] = updates
        return {**order, **updates}

    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(OrderRepo, "update_order", fake_update_order)
    monkeypatch.setattr(order_tracking_service_module.random, "uniform", lambda _a, _b: 7.25)
    monkeypatch.setattr(order_tracking_service_module.random, "randint", lambda _a, _b: 18)

    tracking = await OrderTrackingService.get_tracking_info("12")

    assert tracking.order_id == "12"
    assert tracking.current_location == "at restaurant"
    assert tracking.distance_km == 7.25
    assert tracking.estimated_time_minutes == 18
    assert saved_updates["order_id"] == "12"
    assert saved_updates["updates"] == {"distance": 7.25, "time": 18}


@pytest.mark.asyncio
async def test_refresh_tracking_updates_in_transit_metrics(monkeypatch):
    current_order = {
        "restaurant": "Restaurant_4",
        "customer": "customer_1",
        "driver": "driver_9",
        "order_status": OrderStatus.OUT_FOR_DELIVERY.value,
        "distance": 6.5,
        "time": 20,
    }

    async def fake_get_by_id(_order_id: str):
        return dict(current_order)

    async def fake_update_order(_order_id: str, updates: dict):
        current_order.update(updates)
        return dict(current_order)

    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(OrderRepo, "update_order", fake_update_order)
    monkeypatch.setattr(order_tracking_service_module.random, "uniform", lambda _a, _b: 1.25)
    monkeypatch.setattr(order_tracking_service_module.random, "randint", lambda _a, _b: 4)

    tracking = await OrderTrackingService.refresh_tracking("33")

    assert tracking.current_location == "with driver"
    assert tracking.distance_km == 5.25
    assert tracking.estimated_time_minutes == 16


@pytest.mark.asyncio
async def test_update_tracking_status_marks_order_delivered(monkeypatch):
    current_order = {
        "restaurant": "Restaurant_7",
        "customer": "customer_4",
        "driver": "driver_1",
        "order_status": OrderStatus.OUT_FOR_DELIVERY.value,
        "distance": 3.6,
        "time": 12,
    }

    async def fake_get_by_id(_order_id: str):
        return dict(current_order)

    async def fake_update_order(_order_id: str, updates: dict):
        current_order.update(updates)
        return dict(current_order)

    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(OrderRepo, "update_order", fake_update_order)

    tracking = await OrderTrackingService.update_tracking_status(
        "8",
        OrderTrackingStatusUpdate(order_status=OrderStatus.DELIVERED),
    )

    assert tracking.order_status == OrderStatus.DELIVERED
    assert tracking.current_location == "delivered"
    assert tracking.distance_km == 0.0
    assert tracking.estimated_time_minutes == 0


@pytest.mark.asyncio
async def test_get_tracking_info_raises_when_order_missing(monkeypatch):
    async def fake_get_by_id(_order_id: str):
        return None

    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)

    with pytest.raises(ValueError, match="Order not found"):
        await OrderTrackingService.get_tracking_info("404")


@pytest.mark.asyncio
async def test_get_tracking_info_cancelled_order_is_not_marked_delivered(monkeypatch):
    order = {
        "restaurant": "Restaurant_2",
        "customer": "customer_6",
        "driver": None,
        "order_status": OrderStatus.CANCELLED.value,
        "distance": 4.5,
        "time": 19,
    }

    async def fake_get_by_id(_order_id: str):
        return dict(order)

    async def fake_update_order(_order_id: str, updates: dict):
        order.update(updates)
        return dict(order)

    monkeypatch.setattr(OrderRepo, "get_by_id", fake_get_by_id)
    monkeypatch.setattr(OrderRepo, "update_order", fake_update_order)

    tracking = await OrderTrackingService.get_tracking_info("52")

    assert tracking.order_status == OrderStatus.CANCELLED
    assert tracking.current_location == "cancelled"
    assert tracking.distance_km == 0.0
    assert tracking.estimated_time_minutes == 0
