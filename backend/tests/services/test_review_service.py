import pytest
from pydantic import ValidationError
from src.repositories.rating_repo import RatingRepo
from src.schemas.review_schema import ReportCreate, ReportReason, ReviewCreate, ReviewEdit
from src.services.rating_service import RatingService

@pytest.mark.asyncio
async def test_submit_review_success(monkeypatch):
    order = {'customer_rating': 4, 'food_temperature': 'Hot', 'food_freshness': 5, 'packaging_quality': 1, 'food_condition': 'Fair', 'customer_satisfaction': 3, 'submitted_stars': 5}
    captured = {}

    async def fake_get_by_order_id(_order_id: str):
        return dict(order)

    async def fake_get_restaurant_id_by_order_id(_order_id: str):
        return 16

    async def fake_update_review_text(order_id: str, review_text: str):
        captured['order_id'] = order_id
        captured['review_text'] = review_text
        return {**order, 'review_text': review_text}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    monkeypatch.setattr(RatingRepo, 'get_restaurant_id_by_order_id', fake_get_restaurant_id_by_order_id)
    monkeypatch.setattr(RatingRepo, 'update_review_text', fake_update_review_text)
    result = await RatingService.submit_review('1d8e87M', ReviewCreate(review_text='Great food, fast delivery!'))
    assert result.order_id == '1d8e87M'
    assert result.restaurant_id == 16
    assert result.review_text == 'Great food, fast delivery!'
    assert captured == {'order_id': '1d8e87M', 'review_text': 'Great food, fast delivery!'}

@pytest.mark.asyncio
async def test_submit_review_order_not_found(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return None
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='Order not found'):
        await RatingService.submit_review('FAKE_ORDER_ID', ReviewCreate(review_text='Great food!'))

@pytest.mark.asyncio
async def test_submit_review_already_reviewed(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'review_text': 'Already wrote a review'}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='This order has already been reviewed'):
        await RatingService.submit_review('1d8e87M', ReviewCreate(review_text='Trying again'))

@pytest.mark.asyncio
async def test_submit_review_restaurant_not_found(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'review_text': None}

    async def fake_get_restaurant_id_by_order_id(_order_id: str):
        return None
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    monkeypatch.setattr(RatingRepo, 'get_restaurant_id_by_order_id', fake_get_restaurant_id_by_order_id)
    with pytest.raises(ValueError, match='Restaurant not found for this order'):
        await RatingService.submit_review('1d8e87M', ReviewCreate(review_text='Great food!'))

@pytest.mark.asyncio
async def test_review_schema_rejects_empty_text():
    with pytest.raises(ValidationError):
        ReviewCreate(review_text='')

@pytest.mark.asyncio
async def test_review_schema_accepts_valid_text():
    review = ReviewCreate(review_text='Food was amazing!')
    assert review.review_text == 'Food was amazing!'

@pytest.mark.asyncio
async def test_edit_review_update_both(monkeypatch):
    order = {'submitted_stars': 4, 'review_text': 'Pretty good food'}

    async def fake_get_by_order_id(_order_id: str):
        return dict(order)

    async def fake_update_review_fields(_order_id: str, stars: int | None=None, review_text: str | None=None):
        return {'submitted_stars': stars, 'review_text': review_text}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    monkeypatch.setattr(RatingRepo, 'update_review_fields', fake_update_review_fields)
    result = await RatingService.edit_order_review('1d8e87M', ReviewEdit(stars=5, review_text='Updated review'))
    assert result.order_id == '1d8e87M'
    assert result.submitted_stars == 5
    assert result.review_text == 'Updated review'

@pytest.mark.asyncio
async def test_edit_review_update_stars_only(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'submitted_stars': 4, 'review_text': 'Pretty good food'}

    async def fake_update_review_fields(_order_id: str, stars: int | None=None, review_text: str | None=None):
        return {'submitted_stars': stars, 'review_text': 'Pretty good food' if review_text is None else review_text}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    monkeypatch.setattr(RatingRepo, 'update_review_fields', fake_update_review_fields)
    result = await RatingService.edit_order_review('1d8e87M', ReviewEdit(stars=2))
    assert result.submitted_stars == 2
    assert result.review_text == 'Pretty good food'

@pytest.mark.asyncio
async def test_edit_review_order_not_found(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return None
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='Order not found'):
        await RatingService.edit_order_review('FAKE_ID', ReviewEdit(stars=3))

@pytest.mark.asyncio
async def test_edit_review_no_existing_review(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'submitted_stars': None, 'review_text': None}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='No review exists to edit for this order'):
        await RatingService.edit_order_review('1d8e87M', ReviewEdit(stars=3))

@pytest.mark.asyncio
async def test_edit_review_nothing_to_update(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'submitted_stars': 4, 'review_text': 'Pretty good food'}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='Nothing to update'):
        await RatingService.edit_order_review('1d8e87M', ReviewEdit())

@pytest.mark.asyncio
async def test_delete_review_success(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'submitted_stars': 4, 'review_text': 'Pretty good food'}

    async def fake_delete_review(_order_id: str):
        return {'submitted_stars': None, 'review_text': None}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    monkeypatch.setattr(RatingRepo, 'delete_review', fake_delete_review)
    result = await RatingService.delete_order_review('1d8e87M')
    assert result.order_id == '1d8e87M'
    assert result.message == 'Review and rating deleted successfully'

@pytest.mark.asyncio
async def test_delete_review_order_not_found(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return None
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='Order not found'):
        await RatingService.delete_order_review('FAKE_ID')

@pytest.mark.asyncio
async def test_delete_review_nothing_to_delete(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'submitted_stars': None, 'review_text': None}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='No review exists to delete for this order'):
        await RatingService.delete_order_review('1d8e87M')

@pytest.mark.asyncio
async def test_feedback_prompt_success(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'submitted_stars': None, 'review_text': None}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    result = await RatingService.check_feedback_prompt('1d8e87M')
    assert result.order_id == '1d8e87M'
    assert result.prompt_feedback is True
    assert 'rating and review' in result.message

@pytest.mark.asyncio
async def test_feedback_prompt_order_not_found(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return None
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='Order not found'):
        await RatingService.check_feedback_prompt('FAKE_ID')

@pytest.mark.asyncio
async def test_filter_reviews_no_filter(monkeypatch):
    fake_reviews = [{'order_id': 'abc123', 'submitted_stars': 5, 'review_text': 'Amazing!'}, {'order_id': 'def456', 'submitted_stars': 3, 'review_text': 'Okay'}, {'order_id': 'ghi789', 'submitted_stars': 1, 'review_text': 'Bad'}]

    async def fake_get_restaurant_reviews(_restaurant_id: int, stars: int | None=None):
        assert stars is None
        return fake_reviews
    monkeypatch.setattr(RatingRepo, 'get_restaurant_reviews', fake_get_restaurant_reviews)
    result = await RatingService.get_filtered_reviews(16)
    assert result.restaurant_id == 16
    assert result.stars_filter is None
    assert result.total_reviews == 3
    assert len(result.reviews) == 3

@pytest.mark.asyncio
async def test_filter_reviews_by_stars(monkeypatch):
    fake_reviews = [{'order_id': 'abc123', 'submitted_stars': 5, 'review_text': 'Amazing!'}]

    async def fake_get_restaurant_reviews(_restaurant_id: int, stars: int | None=None):
        assert stars == 5
        return fake_reviews
    monkeypatch.setattr(RatingRepo, 'get_restaurant_reviews', fake_get_restaurant_reviews)
    result = await RatingService.get_filtered_reviews(16, stars=5)
    assert result.stars_filter == 5
    assert result.total_reviews == 1
    assert result.reviews[0].submitted_stars == 5

@pytest.mark.asyncio
async def test_filter_reviews_empty_result(monkeypatch):

    async def fake_get_restaurant_reviews(_restaurant_id: int, stars: int | None=None):
        assert stars == 2
        return []
    monkeypatch.setattr(RatingRepo, 'get_restaurant_reviews', fake_get_restaurant_reviews)
    result = await RatingService.get_filtered_reviews(16, stars=2)
    assert result.total_reviews == 0
    assert result.reviews == []

@pytest.mark.asyncio
async def test_filter_reviews_restaurant_not_found(monkeypatch):

    async def fake_get_restaurant_reviews(_restaurant_id: int, stars: int | None=None):
        assert stars is None
        return None
    monkeypatch.setattr(RatingRepo, 'get_restaurant_reviews', fake_get_restaurant_reviews)
    with pytest.raises(ValueError, match='Restaurant not found'):
        await RatingService.get_filtered_reviews(9999)

@pytest.mark.asyncio
async def test_submit_report_success(monkeypatch):
    order = {'submitted_stars': 5, 'review_text': 'Buy cheap stuff at spam.com'}
    captured = {}

    async def fake_get_by_order_id(_order_id: str):
        return dict(order)

    async def fake_create_report(order_id: str, reason: str, description: str | None=None):
        captured['order_id'] = order_id
        captured['reason'] = reason
        captured['description'] = description
        return {'report_id': 1, 'order_id': order_id, 'reason': reason, 'description': description}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    monkeypatch.setattr(RatingRepo, 'create_report', fake_create_report)
    result = await RatingService.submit_report('1d8e87M', ReportCreate(reason=ReportReason.SPAM))
    assert result.report_id == 1
    assert result.order_id == '1d8e87M'
    assert result.reason == ReportReason.SPAM
    assert result.message == 'Report submitted successfully'
    assert captured == {'order_id': '1d8e87M', 'reason': 'spam', 'description': None}

@pytest.mark.asyncio
async def test_submit_report_with_description(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'submitted_stars': 3, 'review_text': 'Some review'}

    async def fake_create_report(order_id: str, reason: str, description: str | None=None):
        return {'report_id': 3, 'order_id': order_id, 'reason': reason, 'description': description}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    monkeypatch.setattr(RatingRepo, 'create_report', fake_create_report)
    result = await RatingService.submit_report('1d8e87M', ReportCreate(reason=ReportReason.OTHER, description='This review is for the wrong restaurant'))
    assert result.reason == ReportReason.OTHER
    assert result.description == 'This review is for the wrong restaurant'

@pytest.mark.asyncio
async def test_submit_report_order_not_found(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return None
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='Order not found'):
        await RatingService.submit_report('FAKE_ID', ReportCreate(reason=ReportReason.SPAM))

@pytest.mark.asyncio
async def test_submit_report_without_existing_review(monkeypatch):

    async def fake_get_by_order_id(_order_id: str):
        return {'submitted_stars': None, 'review_text': None}
    monkeypatch.setattr(RatingRepo, 'get_by_order_id', fake_get_by_order_id)
    with pytest.raises(ValueError, match='No review exists to report for this order'):
        await RatingService.submit_report('1d8e87M', ReportCreate(reason=ReportReason.SPAM))
