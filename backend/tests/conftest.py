import pytest
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.repositories.user_repo import UserRepo
from src.repositories.order_repo import OrderRepo
from src.api.routers.user_router import router as user_router
from src.api.routers.restaurant_administration_router import (
    router as restaurant_admin_router,
)


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(user_router)
    app.include_router(restaurant_admin_router)
    return app

@pytest.fixture(autouse=True)
def setup_test_files(tmp_path):
    users_file = tmp_path / "users.json"
    orders_file = tmp_path / "orders.json"

    users_file.write_text("{}")
    orders_file.write_text("{}")

    UserRepo.FILE_PATH = users_file
    OrderRepo.FILE_PATH = orders_file

    yield


@pytest.fixture
def client(app):
    return TestClient(app)
