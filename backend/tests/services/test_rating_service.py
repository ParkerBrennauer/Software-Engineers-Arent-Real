import pytest
from pydantic import ValidationError
from src.repositories.rating_repo import RatingRepo
from src.schemas.rating_schema import RatingCreate
from src.services.rating_service import RatingService

@pytest.mark.asyncio
async def test_submit_rating_success(monkeypatch):
    order = {'customer_rating': 4, 'food_temperature': 'Hot', 'food_freshness': 5, 'packaging_quality': 1, 'food_condition': 'Fair', 'customer_satisfaction': 3}
    captured = {}

    async def fake_get_by_order_id(_order_id: str):
        return dict(order)

    async def fake_update_submitted_rating(order_id: str, stars: int):
        captured['order_id'] = order_id
        captured['stars'] = stars
        return {**order, 'submitted_stars': stars}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    monkeypatch.setattr(RatingRepo, 'update_submitted_rating', fake_update_submitted_rating)
    result = await RatingService.submit_rating('1d8e87M', RatingCreate(stars=5))
    assert result.order_id == '1d8e87M'
    assert result.stars == 5
    assert captured == {'order_id': '1d8e87M', 'stars': 5}

@pytest.mark.asyncio
async def test_submit_rating_order_not_found(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return None
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='Order not found'):
        await RatingService.submit_rating('FAKE_ORDER_ID', RatingCreate(stars=3))

@pytest.mark.asyncio
async def test_submit_rating_already_rated(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'submitted_stars': 4}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='This order has already been rated'):
        await RatingService.submit_rating('1d8e87M', RatingCreate(stars=3))

@pytest.mark.asyncio
async def test_rating_schema_rejects_zero_stars():
    with pytest.raises(ValidationError):
        RatingCreate(stars=0)

@pytest.mark.asyncio
async def test_rating_schema_rejects_six_stars():
    with pytest.raises(ValidationError):
        RatingCreate(stars=6)

@pytest.mark.asyncio
async def test_rating_schema_accepts_valid_stars():
    for star_value in range(1, 6):
        rating = RatingCreate(stars=star_value)
        assert rating.stars == star_value
