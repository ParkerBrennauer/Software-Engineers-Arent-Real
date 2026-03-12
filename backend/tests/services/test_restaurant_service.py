import pytest
from src.services.restaurant_services import RestaurantService
from src.repositories.restaurant_repo import RestaurantRepo


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

    # should match 1 and 12, but not 23
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
