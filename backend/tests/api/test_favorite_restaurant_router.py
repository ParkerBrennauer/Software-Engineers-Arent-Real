import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_get_favorite_restaurants_success(client, monkeypatch):
    customer_id = "customer-1"

    def fake_get_current_user():
        return customer_id

    async def fake_get_favorite_restaurants(_customer_id: str):
        return {"customer_id": "customer-1", "favorite_restaurants": [16, 30]}

    monkeypatch.setattr(
        "src.api.routers.customer_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.customer_router.FavoriteRestaurantService.get_favorite_restaurants",
        fake_get_favorite_restaurants,
    )
    response = client.get("/customers/favorites/restaurants")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "customer_id": "customer-1",
        "favorite_restaurants": [16, 30],
    }


@pytest.mark.asyncio
async def test_add_favorite_restaurant_duplicate_returns_conflict(client, monkeypatch):
    customer_id = "customer-1"

    def fake_get_current_user():
        return customer_id

    async def fake_add_favorite_restaurant(_customer_id: str, _restaurant_id: int):
        raise ValueError("Restaurant is already in favorites")

    monkeypatch.setattr(
        "src.api.routers.customer_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.customer_router.FavoriteRestaurantService.add_favorite_restaurant",
        fake_add_favorite_restaurant,
    )
    response = client.post("/customers/favorites/restaurants/16")
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Restaurant is already in favorites"


@pytest.mark.asyncio
async def test_remove_favorite_restaurant_success(client, monkeypatch):
    customer_id = "customer-1"

    def fake_get_current_user():
        return customer_id

    async def fake_remove_favorite_restaurant(_customer_id: str, _restaurant_id: int):
        return {
            "customer_id": "customer-1",
            "restaurant_id": 16,
            "favorite_restaurants": [30],
            "message": "Restaurant removed from favorites",
        }

    monkeypatch.setattr(
        "src.api.routers.customer_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.customer_router.FavoriteRestaurantService.remove_favorite_restaurant",
        fake_remove_favorite_restaurant,
    )
    response = client.delete("/customers/favorites/restaurants/16")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "customer_id": "customer-1",
        "restaurant_id": 16,
        "favorite_restaurants": [30],
        "message": "Restaurant removed from favorites",
    }


@pytest.mark.asyncio
async def test_add_favorite_restaurant_missing_customer_returns_not_found(
    client, monkeypatch
):
    def fake_get_current_user():
        return None

    async def fake_add_favorite_restaurant(_customer_id: str, _restaurant_id: int):
        raise ValueError("Customer not found")

    monkeypatch.setattr(
        "src.api.routers.customer_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.customer_router.FavoriteRestaurantService.add_favorite_restaurant",
        fake_add_favorite_restaurant,
    )
    response = client.post("/customers/favorites/restaurants/16")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No user currently logged in" in response.json()["detail"]
