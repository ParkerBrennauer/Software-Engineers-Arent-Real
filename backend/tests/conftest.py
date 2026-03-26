import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.routers.user_router import router as user_router
from src.api.routers.restaurant_administration_router import (
    router as restaurant_admin_router,
)
from src.api.routers.order_router import router as order_router
from src.api.routers.rating_router import router as rating_router
from src.api.dependencies import setup_exception_handlers


@pytest.fixture
def app():
    app = FastAPI()
    setup_exception_handlers(app)
    app.include_router(user_router)
    app.include_router(restaurant_admin_router)
    app.include_router(order_router)
    app.include_router(rating_router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)
