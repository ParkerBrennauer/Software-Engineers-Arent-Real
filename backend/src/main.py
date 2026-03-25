from fastapi import FastAPI

from src.api.routers.rating_router import router as rating_router
from src.api.routers.order_router import router as order_router
from src.api.routers.restaurant_administration_router import (
    router as restaurant_administration_router,
)
from src.api.routers.user_router import router as user_router

app = FastAPI(title="Software Engineers Aren't Real Backend")

app.include_router(user_router)
app.include_router(restaurant_administration_router)
app.include_router(rating_router)
app.include_router(order_router)
