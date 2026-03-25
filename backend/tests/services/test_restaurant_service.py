import pytest
from src.services.restaurant_services import RestaurantService
from src.repositories.restaurant_repo import RestaurantRepo
from src.schemas.restaurant_schema import RestaurantCreate, RestaurantUpdate

from src.services.item_services import ItemService
from src.schemas.item_schema import ItemCreate


@pytest.mark.asyncio
async def test_get_all_restaurants_returns_mocked_data(monkeypatch):
    test_data = [
        {"restaurant_id": 1, "cuisine": "Italian", "avg_ratings": 4.2},
        {"restaurant_id": 12, "cuisine": "Japanese", "avg_ratings": 4.8},
        {"restaurant_id": 23, "cuisine": "Mexican", "avg_ratings": 3.9},
    ]

    async def test_read_all():
        return test_data

    monkeypatch.setattr(RestaurantRepo, "read_all", test_read_all)

    results = await RestaurantService.get_all_restaurants()

    assert results == test_data


@pytest.mark.asyncio
async def test_get_restaurants_search_matches_substring_of_id(monkeypatch):
    test_data = [
        {"restaurant_id": 1, "cuisine": "Italian", "avg_ratings": 4.2},
        {"restaurant_id": 12, "cuisine": "Japanese", "avg_ratings": 4.8},
        {"restaurant_id": 23, "cuisine": "Mexican", "avg_ratings": 3.9},
    ]

    async def test_read_all():
        return test_data

    monkeypatch.setattr(RestaurantRepo, "read_all", test_read_all)

    results = await RestaurantService.get_restaurants_search("1")

    assert [r["restaurant_id"] for r in results] == [1, 12]


@pytest.mark.asyncio
async def test_search_advance_filters_and_sorts_by_rating_asc(monkeypatch):
    test_data = [
        {"restaurant_id": 1, "cuisine": "Italian", "avg_ratings": 4.2},
        {"restaurant_id": 12, "cuisine": "Italian", "avg_ratings": 4.8},
        {"restaurant_id": 21, "cuisine": "Mexican", "avg_ratings": 3.9},
    ]

    async def test_read_all():
        return test_data

    monkeypatch.setattr(RestaurantRepo, "read_all", test_read_all)

    results = await RestaurantService.get_restaurants_search_advance(
        query="1",
        filters=["Italian"],
        sort="RatingAsc",
    )

    assert [r["restaurant_id"] for r in results] == [1, 12]


@pytest.mark.asyncio
async def test_get_restaurant_menu_returns_menu(monkeypatch):
    restaurants_data = [
        {"restaurant_id": 10, "cuisine": "Indian"},
        {"restaurant_id": 16, "cuisine": "Mexican"},
    ]

    async def fake_read_all():
        return restaurants_data

    async def fake_get_items_by_restaurant_id(restaurant_id: int):
        assert restaurant_id == 16
        return [
            {"item_name": "Tacos", "restaurant_id": 16},
            {"item_name": "Burrito", "restaurant_id": 16},
        ]

    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)
    monkeypatch.setattr(ItemService, "get_items_by_restaurant_id",
                        fake_get_items_by_restaurant_id)

    result = await RestaurantService.get_restaurant_menu(16)

    assert result == [
        {"item_name": "Tacos", "restaurant_id": 16},
        {"item_name": "Burrito", "restaurant_id": 16},
    ]


@pytest.mark.asyncio
async def test_get_restaurant_menu_and_not_found(monkeypatch):
    restaurants_data = [
        {"restaurant_id": 10, "cuisine": "Indian"},
    ]

    async def fake_read_all():
        return restaurants_data

    async def fake_get_items_by_restaurant_id(_restaurant_id: int):
        raise AssertionError(
            "Should not call ItemService if restaurant doesn't exist")

    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)
    monkeypatch.setattr(ItemService, "get_items_by_restaurant_id",
                        fake_get_items_by_restaurant_id)

    with pytest.raises(ValueError) as excinfo:
        await RestaurantService.get_restaurant_menu(999)

    assert str(excinfo.value) == "Restaurant not found"


@pytest.mark.asyncio
async def test_create_restaurant_writes_through_repo(monkeypatch):
    existing_restaurants = [
        {
            "id": 1,
            "restaurant_id": 10,
            "cuisine": "Italian",
            "ratings": {"taste": 4},
            "orders": [],
            "menu": [],
        },
        {
            "id": 2,
            "restaurant_id": 20,
            "cuisine": "Japanese",
            "ratings": {"taste": 5},
            "orders": [],
            "menu": [],
        },
    ]

    async def fake_read_all():
        return existing_restaurants.copy()

    async def fake_write_restaurant(data):  # pylint: disable=unused-argument
        None

    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)
    monkeypatch.setattr(RestaurantRepo, "write_restaurant", fake_write_restaurant)

    restaurant_in = RestaurantCreate(
        cuisine="Mexican",
    )

    result = await RestaurantService.create_restaurant(restaurant_in)

    assert result == {
        "id": 3,
        "cuisine": "Mexican",
        "menu": [],
        "ratings": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
        "orders": []
    }


@pytest.mark.asyncio
async def test_update_restaurant_writes_through_repo(monkeypatch):
    existing_restaurants = [
        {
            "id": 1,
            "restaurant_id": 1,
            "cuisine": "Italian",
            "ratings": {"taste": 4},
            "orders": [],
            "menu": [
                {
                    "item_name": "Pasta",
                    "restaurant_id": 1,
                    "cost": 15.0,
                    "cuisine": "Italian",
                    "times_ordered": 20,
                    "avg_rating": 4.4,
                    "dietary": {},
                }
            ],
        },
        {
            "id": 2,
            "restaurant_id": 2,
            "cuisine": "Japanese",
            "ratings": {"taste": 5},
            "orders": [],
            "menu": [
                {
                    "item_name": "Sushi",
                    "restaurant_id": 2,
                    "cost": 18.0,
                    "cuisine": "Japanese",
                    "times_ordered": 30,
                    "avg_rating": 4.8,
                    "dietary": {},
                }
            ],
        },
    ]

    async def fake_read_all():
        return [r.copy() for r in existing_restaurants]

    async def fake_write_restaurant(data):  # pylint: disable=unused-argument
        pass

    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)
    monkeypatch.setattr(RestaurantRepo, "write_restaurant",
                        fake_write_restaurant)

    restaurant_update = RestaurantUpdate(
        cuisine="Thai",
        menu=[
            ItemCreate(
                item_name="Pad Thai",
                restaurant_id=2,
                cost=16.5,
                cuisine="Thai",
            ),
            ItemCreate(
                item_name="Tom Yum",
                restaurant_id=2,
                cost=11.0,
                cuisine="Thai",
            ),
        ],
    )

    result = await RestaurantService.update_restaurant(2, restaurant_update)

    assert result == {
        "id": 2,
        "restaurant_id": 2,
        "cuisine": "Thai",
        "ratings": {"taste": 5},
        "orders": [],
        "menu": [
            {
                "item_name": "Pad Thai",
                "restaurant_id": 2,
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
                    "kosher": False
                },
            },
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
                    "kosher": False
                },
            },
        ],
    }


@pytest.mark.asyncio
async def test_update_restaurant_raises_when_not_found(monkeypatch):
    existing_restaurants = [
        {
            "id": 1,
            "restaurant_id": 1,
            "cuisine": "Italian",
            "ratings": {"taste": 4},
            "orders": [],
            "menu": [],
        },
        {
            "id": 2,
            "restaurant_id": 2,
            "cuisine": "Japanese",
            "ratings": {"taste": 5},
            "orders": [],
            "menu": [],
        },
    ]

    async def fake_read_all():
        return [r.copy() for r in existing_restaurants]

    async def fake_write_restaurant(_data):  # pylint: disable=unused-argument
        pytest.fail(
            "write_restaurant should not be called when restaurant is not found")

    monkeypatch.setattr(RestaurantRepo, "read_all", fake_read_all)
    monkeypatch.setattr(RestaurantRepo, "write_restaurant",
                        fake_write_restaurant)

    restaurant_update = RestaurantUpdate(
        cuisine="Thai",
        menu=[
            ItemCreate(
                item_name="Pad Thai",
                restaurant_id=999,
                cost=16.5,
                cuisine="Thai",
            )
        ],
    )

    with pytest.raises(ValueError, match="Restaurant not found"):
        await RestaurantService.update_restaurant(999, restaurant_update)
