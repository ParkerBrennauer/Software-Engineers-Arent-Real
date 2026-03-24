import pytest
from src.services.item_services import ItemService
from src.repositories.item_repo import ItemRepo


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
