from fastapi.testclient import TestClient

from src.main import app
from src.services.restaurant_services import RestaurantService

client = TestClient(app)


def test_create_restaurant_success(monkeypatch):
    async def fake_create_restaurant(_restaurant_in):
        return {
            "id": 3,
            "restaurant_id": 3,
            "cuisine": "Thai",
            "menu": [
                {
                    "item_name": "Pad Thai",
                    "restaurant_id": 3,
                    "cost": 16.5,
                    "cuisine": "Thai",
                    "times_ordered": 0,
                    "avg_rating": 0.0,
                    "dietary": {
                        "vegan": False,
                        "vegetarian": False,
                        "gluten_free": False,
                        "dairy_free": False,
                        "nut_free": False,
                        "halal": False,
                        "kosher": False,
                    },
                }
            ],
        }

    monkeypatch.setattr(
        RestaurantService, "create_restaurant", fake_create_restaurant
    )

    response = client.post(
        "/restaurants",
        json={
            "cuisine": "Thai",
            "menu": [
                {
                    "item_name": "Pad Thai",
                    "restaurant_id": 3,
                    "cost": 16.5,
                    "cuisine": "Thai",
                    "times_ordered": 0,
                    "avg_rating": 0.0,
                    "dietary": {
                        "vegan": False,
                        "vegetarian": False,
                        "gluten_free": False,
                        "dairy_free": False,
                        "nut_free": False,
                        "halal": False,
                        "kosher": False,
                    },
                }
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 3
    assert data["restaurant_id"] == 3
    assert data["cuisine"] == "Thai"


def test_create_restaurant_returns_exists(monkeypatch):
    async def fake_create_restaurant(_restaurant_in):
        raise ValueError("Restaurant already exists")

    monkeypatch.setattr(
        RestaurantService, "create_restaurant", fake_create_restaurant
    )

    response = client.post(
        "/restaurants",
        json={
            "cuisine": "Thai",
            "menu": [
                {
                    "item_name": "Pad Thai",
                    "restaurant_id": 3,
                    "cost": 16.5,
                    "cuisine": "Thai",
                    "times_ordered": 0,
                    "avg_rating": 0.0,
                    "dietary": {
                        "vegan": False,
                        "vegetarian": False,
                        "gluten_free": False,
                        "dairy_free": False,
                        "nut_free": False,
                        "halal": False,
                        "kosher": False,
                    },
                }
            ],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Restaurant already exists"


def test_update_restaurant_success(monkeypatch):
    async def fake_update_restaurant(_restaurant_id: int, _restaurant_in):
        return {
            "id": 2,
            "restaurant_id": 2,
            "cuisine": "Thai",
            "ratings": {"taste": 5},
            "orders": [],
            "menu": [
                {
                    "item_name": "Tom Yum",
                    "restaurant_id": 2,
                    "cost": 11.0,
                    "cuisine": "Thai",
                    "times_ordered": 0,
                    "avg_rating": 0.0,
                    "dietary": {
                        "vegan": False,
                        "vegetarian": False,
                        "gluten_free": False,
                        "dairy_free": False,
                        "nut_free": False,
                        "halal": False,
                        "kosher": False,
                    },
                }
            ],
        }

    monkeypatch.setattr(
        RestaurantService, "update_restaurant", fake_update_restaurant
    )

    response = client.patch(
        "/restaurants/2",
        json={
            "cuisine": "Thai",
            "menu": [
                {
                    "item_name": "Tom Yum",
                    "restaurant_id": 2,
                    "cost": 11.0,
                    "cuisine": "Thai",
                    "times_ordered": 0,
                    "avg_rating": 0.0,
                    "dietary": {
                        "vegan": False,
                        "vegetarian": False,
                        "gluten_free": False,
                        "dairy_free": False,
                        "nut_free": False,
                        "halal": False,
                        "kosher": False,
                    },
                }
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert data["restaurant_id"] == 2
    assert data["cuisine"] == "Thai"


def test_update_restaurant_returns_not_found(monkeypatch):
    async def fake_update_restaurant(_restaurant_id: int, _restaurant_in):
        raise ValueError("Restaurant not found")

    monkeypatch.setattr(
        RestaurantService, "update_restaurant", fake_update_restaurant
    )

    response = client.patch(
        "/restaurants/999",
        json={
            "cuisine": "Thai",
            "menu": [
                {
                    "item_name": "Tom Yum",
                    "restaurant_id": 999,
                    "cost": 11.0,
                    "cuisine": "Thai",
                    "times_ordered": 0,
                    "avg_rating": 0.0,
                    "dietary": {
                        "vegan": False,
                        "vegetarian": False,
                        "gluten_free": False,
                        "dairy_free": False,
                        "nut_free": False,
                        "halal": False,
                        "kosher": False,
                    },
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"


def test_update_restaurant_returns_value_error(monkeypatch):
    async def fake_update_restaurant(_restaurant_id: int, _restaurant_in):
        raise ValueError("Invalid menu data")

    monkeypatch.setattr(
        RestaurantService, "update_restaurant", fake_update_restaurant
    )

    response = client.patch(
        "/restaurants/2",
        json={
            "cuisine": "Thai",
            "menu": [
                {
                    "item_name": "Tom Yum",
                    "restaurant_id": 2,
                    "cost": 11.0,
                    "cuisine": "Thai",
                    "times_ordered": 0,
                    "avg_rating": 0.0,
                    "dietary": {
                        "vegan": False,
                        "vegetarian": False,
                        "gluten_free": False,
                        "dairy_free": False,
                        "nut_free": False,
                        "halal": False,
                        "kosher": False,
                    },
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid menu data"