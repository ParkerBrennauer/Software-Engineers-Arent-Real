from fastapi.testclient import TestClient
from src.main import app
from src.schemas.order_schema import OrderStatus
from src.schemas.order_tracking_schema import OrderTrackingResponse, OrderTrackingStatusUpdate
from src.services.order_tracking_service import OrderTrackingService
client = TestClient(app)

def test_get_order_tracking_returns_tracking_payload(monkeypatch):

    async def fake_get_tracking_info(_order_id: str):
        return OrderTrackingResponse(order_id='21', restaurant='Restaurant_1', customer='customer_1', driver='driver_1', order_status=OrderStatus.OUT_FOR_DELIVERY, current_location='with driver', distance_km=4.3, estimated_time_minutes=14, status_message='Your order is on the way to the drop-off location.')
    monkeypatch.setattr(OrderTrackingService, 'get_tracking_info', fake_get_tracking_info)
    response = client.get('/orders/21/tracking')
    assert response.status_code == 200
    assert response.json()['distance_km'] == 4.3
    assert response.json()['current_location'] == 'with driver'

def test_update_order_tracking_status_returns_404_for_missing_order(monkeypatch):

    async def fake_update_tracking_status(_order_id: str, _tracking_update: OrderTrackingStatusUpdate):
        raise ValueError('Order not found')
    monkeypatch.setattr(OrderTrackingService, 'update_tracking_status', fake_update_tracking_status)
    response = client.patch('/orders/999/tracking/status', json={'order_status': OrderStatus.DELIVERED.value})
    assert response.status_code == 404
    assert response.json()['detail'] == 'Order not found'
