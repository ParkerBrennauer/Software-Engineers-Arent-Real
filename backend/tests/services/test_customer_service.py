import pytest

from src.repositories.item_repo import ItemRepo
from src.repositories.user_repo import UserRepo
from src.services.customer_service import CustomerService


@pytest.mark.asyncio
async def test_toggle_favourite_removes_existing_item(monkeypatch):
    captured = {}

    async def fake_get_by_username(_username: str):
        return {"username": "alice", "favourites": ["Burger_1", "Pizza_2"]}

    async def fake_get_by_key(item_key: str):
        if item_key == "Burger_1":
            return {"restaurant_id": 1}
        if item_key == "Pizza_2":
            return {"restaurant_id": 2}
        return None

    async def fake_update_by_username(username: str, updates: dict):
        captured["username"] = username
        captured["updates"] = updates
        return {"username": username, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(ItemRepo, "get_by_key", fake_get_by_key)
    monkeypatch.setattr(UserRepo, "update_by_username",
                        fake_update_by_username)

    result = await CustomerService.toggle_favourite("alice", "Burger_1")

    assert result == "removed"
    assert captured == {
        "username": "alice",
        "updates": {"favourites": ["Pizza_2"]},
    }


@pytest.mark.asyncio
async def test_toggle_favourite_adds_when_no_same_restaurant(monkeypatch):
    captured = {}

    async def fake_get_by_username(_username: str):
        return {"username": "alice", "favourites": ["Sushi_2"]}

    async def fake_get_by_key(item_key: str):
        item_map = {
            "Sushi_2": {"restaurant_id": 2},
            "Burger_1": {"restaurant_id": 1},
        }
        return item_map.get(item_key)

    async def fake_update_by_username(username: str, updates: dict):
        captured["username"] = username
        captured["updates"] = updates
        return {"username": username, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(ItemRepo, "get_by_key", fake_get_by_key)
    monkeypatch.setattr(UserRepo, "update_by_username",
                        fake_update_by_username)

    result = await CustomerService.toggle_favourite("alice", "Burger_1")

    assert result == "added"
    assert captured == {
        "username": "alice",
        "updates": {"favourites": ["Sushi_2", "Burger_1"]},
    }


@pytest.mark.asyncio
async def test_toggle_favourite_replaces_same_restaurant(monkeypatch):
    captured = {}

    async def fake_get_by_username(_username: str):
        return {"username": "alice", "favourites": ["Salad_1", "Pizza_2"]}

    async def fake_get_by_key(item_key: str):
        item_map = {
            "Salad_1": {"restaurant_id": 1},
            "Pizza_2": {"restaurant_id": 2},
            "Burger_1": {"restaurant_id": 1},
        }
        return item_map.get(item_key)

    async def fake_update_by_username(username: str, updates: dict):
        captured["username"] = username
        captured["updates"] = updates
        return {"username": username, **updates}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(ItemRepo, "get_by_key", fake_get_by_key)
    monkeypatch.setattr(UserRepo, "update_by_username",
                        fake_update_by_username)

    result = await CustomerService.toggle_favourite("alice", "Burger_1")

    assert result == "replaced"
    assert captured == {
        "username": "alice",
        "updates": {"favourites": ["Pizza_2", "Burger_1"]},
    }


@pytest.mark.asyncio
async def test_toggle_favourite_validates_inputs(monkeypatch):
    async def fake_get_by_username(_username: str):
        return {"username": "alice", "favourites": []}

    async def fake_get_by_key(_item_key: str):
        return {"restaurant_id": 1}

    monkeypatch.setattr(UserRepo, "get_by_username", fake_get_by_username)
    monkeypatch.setattr(ItemRepo, "get_by_key", fake_get_by_key)

    with pytest.raises(ValueError, match="Username is empty"):
        await CustomerService.toggle_favourite("", "Burger_1")

    with pytest.raises(ValueError, match="itemKey is empty"):
        await CustomerService.toggle_favourite("alice", "")


@pytest.mark.asyncio
async def test_toggle_favourite_user_or_item_not_found(monkeypatch):
    async def fake_missing_user(_username: str):
        return None

    async def fake_user(_username: str):
        return {"username": "alice", "favourites": []}

    async def fake_missing_item(_item_key: str):
        return None

    monkeypatch.setattr(UserRepo, "get_by_username", fake_missing_user)
    with pytest.raises(ValueError, match="User not found"):
        await CustomerService.toggle_favourite("alice", "Burger_1")

    monkeypatch.setattr(UserRepo, "get_by_username", fake_user)
    monkeypatch.setattr(ItemRepo, "get_by_key", fake_missing_item)
    with pytest.raises(ValueError, match="Item not found"):
        await CustomerService.toggle_favourite("alice", "Burger_1")
