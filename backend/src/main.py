from fastapi import FastAPI
from src.api.routers.customer_router import router as customer_router
from src.api.routers.restaurant_router import router as restaurant_router
from src.api.routers.item_router import router as item_router
from src.api.routers.rating_router import router as rating_router
from src.api.routers.order_router import router as order_router
from src.api.routers.restaurant_administration_router import (
    router as restaurant_administration_router,
)
from src.api.routers.user_router import router as user_router
from src.api.dependencies import setup_exception_handlers

app = FastAPI(title="Software Engineers Aren't Real Backend")

setup_exception_handlers(app)

app.include_router(customer_router)
app.include_router(user_router)
app.include_router(restaurant_administration_router)
app.include_router(rating_router)
app.include_router(order_router)
app.include_router(item_router)
app.include_router(restaurant_router)
