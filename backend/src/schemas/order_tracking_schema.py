from pydantic import BaseModel, Field
from src.schemas.order_schema import OrderStatus

class OrderTrackingStatusUpdate(BaseModel):
    order_status: OrderStatus
    driver: str | None = None

class OrderTrackingResponse(BaseModel):
    order_id: str
    restaurant: str
    customer: str
    driver: str | None = None
    order_status: OrderStatus
    delivery_instructions: str | None = None
    current_location: str
    distance_km: float
    estimated_time_minutes: int
    status_message: str
    shared_with: list[str] = Field(default_factory=lambda: ['customer', 'driver', 'restaurant'])
