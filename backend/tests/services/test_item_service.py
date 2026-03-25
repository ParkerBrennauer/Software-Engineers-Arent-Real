import pytest
from src.services.item_services import ItemService
from src.repositories.item_repo import ItemRepo
from src.schemas.item_schema import ItemUpdate, ItemCreate, ItemRestrictions


@pytest.mark.asyncio
async def test_get_item_by_key(monkeypatch):
    test_data = {
        "Briyani_20": {
            "food_item": "Briyani",
            "restaurant_id": 20,
            "times_ordered": 2,
            "avg_rating": 4.3
        },
        "Tacos_6": {
            "food_item": "Taccos",
            "restaurant_id": 6,
            "times_ordered": 8,
            "avg_rating": 3.9
        },
        "Shawarma_78": {
            "food_item": "Shawarma",
            "restaurant_id": 78,
            "times_ordered": 3,
            "avg_rating": 4.6
        },
    }

    async def test_read_all():
        return test_data

    monkeypatch.setattr(ItemRepo, "read_all", test_read_all)

    results = await ItemService.get_items_by_key("Tacos_6")

    assert results == {"food_item": "Taccos",
                       "restaurant_id": 6, "times_ordered": 8, "avg_rating": 3.9}


@pytest.mark.asyncio
async def test_get_items_by_restaurant_id(monkeypatch):
    test_data = {
        "Briyani_20": {
            "food_item": "Briyani",
            "restaurant_id": 10,
            "times_ordered": 2,
            "avg_rating": 4.3
        },
        "Tacos_6": {
            "food_item": "Taccos",
            "restaurant_id": 6,
            "times_ordered": 8,
            "avg_rating": 3.9
        },
        "Shawarma_78": {
            "food_item": "Shawarma",
            "restaurant_id": 10,
            "times_ordered": 3,
            "avg_rating": 4.6
        },
    }

    async def test_read_all():
        return test_data

    monkeypatch.setattr(ItemRepo, "read_all", test_read_all)

    results = await ItemService.get_items_by_restaurant_id(10)

    assert results == [
        {"food_item": "Briyani", "restaurant_id": 10,
            "times_ordered": 2, "avg_rating": 4.3},
        {"food_item": "Shawarma", "restaurant_id": 10,
            "times_ordered": 3, "avg_rating": 4.6}
    ]


@pytest.mark.asyncio
async def test_update_item_by_key_unchanged(monkeypatch):
    test_data = {
        "Tacos_16": {
            "item_name": "Tacos",
            "restaurant_id": 16,
            "times_ordered": 8,
            "avg_rating": 3.625,
            "cost": 10.0,
            "cuisine": "Mexican",
            "dietary": {"vegan": False, "gluten_free": False}
        }
    }

    async def fake_read_all(cls):  # pylint: disable=unused-argument
        return test_data

    async def fake_write_all(cls, data):  # pylint: disable=unused-argument
        return None

    monkeypatch.setattr(ItemRepo, "read_all", classmethod(fake_read_all))
    monkeypatch.setattr(ItemRepo, "write_all", classmethod(fake_write_all))

    updates = ItemUpdate(cost=12.5, cuisine="Tex-Mex")

    result = await ItemService.update_item_by_key("Tacos_16", updates)

    assert result == {
        "item_name": "Tacos",
        "restaurant_id": 16,
        "times_ordered": 8,
        "avg_rating": 3.625,
        "cost": 12.5,
        "cuisine": "Tex-Mex",
        "dietary": {"vegan": False, "gluten_free": False},
        "key": "Tacos_16"
    }


@pytest.mark.asyncio
async def test_update_item_by_key_changed(monkeypatch):
    test_data = {
        "Tacos_16": {
            "item_name": "Tacos",
            "restaurant_id": 16,
            "times_ordered": 8,
            "avg_rating": 3.625,
            "cost": 10.0,
            "cuisine": "Mexican",
            "dietary": {"vegan": False, "gluten_free": False}
        }
    }

    async def fake_read_all(cls):  # pylint: disable=unused-argument
        return test_data

    async def fake_write_all(cls, data):  # pylint: disable=unused-argument
        return None

    monkeypatch.setattr(ItemRepo, "read_all", classmethod(fake_read_all))
    monkeypatch.setattr(ItemRepo, "write_all", classmethod(fake_write_all))

    updates = ItemUpdate(item_name="Taco")

    result = await ItemService.update_item_by_key("Tacos_16", updates)

    assert result == {
        "item_name": "Taco",
        "restaurant_id": 16,
        "times_ordered": 8,
        "avg_rating": 3.625,
        "cost": 10.0,
        "cuisine": "Mexican",
        "dietary": {"vegan": False, "gluten_free": False},
        "key": "Taco_16"
    }


@pytest.mark.asyncio
async def test_update_item_updates_dietary(monkeypatch):
    test_data = {
        "Tacos_16": {
            "item_name": "Tacos",
            "restaurant_id": 16,
            "times_ordered": 8,
            "avg_rating": 3.625,
            "cost": 10.0,
            "cuisine": "Mexican",
            "dietary": {"vegan": False, "gluten_free": False}
        }
    }

    async def fake_read_all(cls):  # pylint: disable=unused-argument
        return test_data

    async def fake_write_all(cls, data):  # pylint: disable=unused-argument
        return None

    monkeypatch.setattr(ItemRepo, "read_all", classmethod(fake_read_all))
    monkeypatch.setattr(ItemRepo, "write_all", classmethod(fake_write_all))

    dietary = ItemRestrictions(vegan=True, gluten_free=True)
    updates = ItemUpdate(dietary=dietary)

    result = await ItemService.update_item_by_key("Tacos_16", updates)

    expected_item = {
        "item_name": "Tacos",
        "restaurant_id": 16,
        "times_ordered": 8,
        "avg_rating": 3.625,
        "cost": 10.0,
        "cuisine": "Mexican",
        "dietary": {"vegan": True, "gluten_free": True},
        "key": "Tacos_16"
    }

    assert result == expected_item

@pytest.mark.asyncio
async def test_create_item_creates_new_item(monkeypatch):
    test_data = {}

    async def fake_read_all(cls):  # pylint: disable=unused-argument
        return test_data

    async def fake_write_all(cls, data):  # pylint: disable=unused-argument
        return None

    monkeypatch.setattr(ItemRepo, "read_all", classmethod(fake_read_all))
    monkeypatch.setattr(ItemRepo, "write_all", classmethod(fake_write_all))

    dietary = ItemRestrictions(vegan=True, gluten_free=True)
    item_in = ItemCreate(item_name="Tacos", restaurant_id=16, cost=10.0, cuisine="Mexican", dietary=dietary)

    result = await ItemService.create_item(item_in)

    expected_saved_item = {
        "item_name": "Tacos",
        "restaurant_id": 16,
        "times_ordered": 0,
        "avg_rating": 0.0,
        "cost": 10.0,
        "cuisine": "Mexican",
        "dietary": {
            "vegan": True,
            "vegetarian": False,
            "gluten_free": True,
            "dairy_free": False,
            "nut_free": False,
            "halal": False,
            "kosher": False
        },
    }

    assert result == expected_saved_item


@pytest.mark.asyncio
async def test_create_item_and_item_exists(monkeypatch):
    async def fake_get_by_key(item_key: str):
        return {
            "item_name": "Tacos",
            "restaurant_id": 16,
            "cost": 10.0,
            "cuisine": "Mexican",
            "dietary": {"vegan": False, "gluten_free": False},
        }

    async def fake_save_item(item_data: dict):
        raise AssertionError(
            "save_item should not be called when item already exists")

    monkeypatch.setattr(ItemRepo, "get_by_key", fake_get_by_key)
    monkeypatch.setattr(ItemRepo, "save_item", fake_save_item)

    item_in = ItemCreate(
        item_name="Tacos",
        restaurant_id=16,
        cost=10.0,
        cuisine="Mexican",
        dietary=ItemRestrictions(vegan=True, gluten_free=True),
    )

    with pytest.raises(ValueError) as excinfo:
        await ItemService.create_item(item_in)

    assert str(excinfo.value) == "Item already exists"
