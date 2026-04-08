import httpx
import pytest
from src.main import app
from src.schemas.review_schema import (
    DeleteResponse,
    ReportCreate,
    ReportResponse,
    ReviewCreate,
    ReviewEdit,
    ReviewEditResponse,
    ReviewResponse,
)
from src.services.rating_service import RatingService
from src.services.user_service import UserService
from src.repositories.rating_repo import RatingRepo


@pytest.mark.asyncio
async def test_submit_review_success(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_submit_review(_order_id: str, _payload: ReviewCreate):
        return ReviewResponse(
            order_id="1d8e87M",
            restaurant_id=16,
            review_text="Great food, fast delivery!",
        )

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "submit_review", fake_submit_review)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/1d8e87M/review", json={"review_text": "Great food, fast delivery!"}
        )
    assert response.status_code == 200
    assert response.json() == {
        "order_id": "1d8e87M",
        "restaurant_id": 16,
        "review_text": "Great food, fast delivery!",
    }


@pytest.mark.asyncio
async def test_submit_review_order_not_found(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/NONEXISTENT_ORDER/review", json={"review_text": "Great food!"}
        )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_submit_review_permission_denied(monkeypatch):

    def fake_get_current_user():
        return "customer2"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/1d8e87M/review", json={"review_text": "Great food!"}
        )
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


@pytest.mark.asyncio
async def test_submit_review_duplicate(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_submit_review(_order_id: str, _payload: ReviewCreate):
        raise ValueError("This order has already been reviewed")

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "submit_review", fake_submit_review)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/1d8e87M/review", json={"review_text": "Trying again"}
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "This order has already been reviewed"


@pytest.mark.asyncio
async def test_submit_review_restaurant_not_found(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_submit_review(_order_id: str, _payload: ReviewCreate):
        raise ValueError("Restaurant not found for this order")

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "submit_review", fake_submit_review)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/orders/1d8e87M/review", json={"review_text": "Great food!"}
        )
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found for this order"


@pytest.mark.asyncio
async def test_submit_review_invalid_text():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/orders/1d8e87M/review", json={"review_text": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_edit_review_success(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_edit_order_review(_order_id: str, _payload: ReviewEdit):
        return ReviewEditResponse(
            order_id="1d8e87M", submitted_stars=5, review_text="Updated review"
        )

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "edit_order_review", fake_edit_order_review)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.put(
            "/orders/1d8e87M/review", json={"stars": 5, "review_text": "Updated review"}
        )
    assert response.status_code == 200
    assert response.json() == {
        "order_id": "1d8e87M",
        "submitted_stars": 5,
        "review_text": "Updated review",
    }


@pytest.mark.asyncio
async def test_edit_review_order_not_found(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.put("/orders/FAKE_ID/review", json={"stars": 3})
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_edit_review_permission_denied(monkeypatch):

    def fake_get_current_user():
        return "customer2"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.put("/orders/1d8e87M/review", json={"stars": 3})
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


@pytest.mark.asyncio
async def test_edit_review_no_existing_review(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_edit_order_review(_order_id: str, _payload: ReviewEdit):
        raise ValueError("No review exists to edit for this order")

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "edit_order_review", fake_edit_order_review)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.put("/orders/1d8e87M/review", json={"stars": 3})
    assert response.status_code == 400
    assert response.json()["detail"] == "No review exists to edit for this order"


@pytest.mark.asyncio
async def test_edit_review_nothing_to_update(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_edit_order_review(_order_id: str, _payload: ReviewEdit):
        raise ValueError("Nothing to update")

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "edit_order_review", fake_edit_order_review)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.put("/orders/1d8e87M/review", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Nothing to update"


@pytest.mark.asyncio
async def test_delete_review_success(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_delete_order_review(_order_id: str):
        return DeleteResponse(
            order_id="1d8e87M", message="Review and rating deleted successfully"
        )

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "delete_order_review", fake_delete_order_review)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.delete("/orders/1d8e87M/review")
    assert response.status_code == 200
    assert response.json() == {
        "order_id": "1d8e87M",
        "message": "Review and rating deleted successfully",
    }


@pytest.mark.asyncio
async def test_delete_review_order_not_found(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.delete("/orders/FAKE_ID/review")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_delete_review_permission_denied(monkeypatch):

    def fake_get_current_user():
        return "customer2"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.delete("/orders/1d8e87M/review")
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


@pytest.mark.asyncio
async def test_delete_review_nothing_to_delete(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_delete_order_review(_order_id: str):
        raise ValueError("No review exists to delete for this order")

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "delete_order_review", fake_delete_order_review)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.delete("/orders/1d8e87M/review")
    assert response.status_code == 400
    assert response.json()["detail"] == "No review exists to delete for this order"


@pytest.mark.asyncio
async def test_report_review_success(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_submit_report(_order_id: str, _payload: ReportCreate):
        return ReportResponse(
            report_id=1,
            order_id="1d8e87M",
            reason="spam",
            description=None,
            message="Report submitted successfully",
        )

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "submit_report", fake_submit_report)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/orders/1d8e87M/report", json={"reason": "spam"})
    assert response.status_code == 200
    assert response.json() == {
        "report_id": 1,
        "order_id": "1d8e87M",
        "reason": "spam",
        "description": None,
        "message": "Report submitted successfully",
    }


@pytest.mark.asyncio
async def test_report_review_order_not_found(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/orders/FAKE_ID/report", json={"reason": "spam"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_report_review_permission_denied(monkeypatch):

    def fake_get_current_user():
        return "customer2"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/orders/1d8e87M/report", json={"reason": "spam"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


@pytest.mark.asyncio
async def test_report_review_without_existing_review(monkeypatch):

    def fake_get_current_user():
        return "customer1"

    async def fake_get_by_order_id(_order_id: str):
        return {"id": _order_id, "customer": "customer1"}

    async def fake_submit_report(_order_id: str, _payload: ReportCreate):
        raise ValueError("No review exists to report for this order")

    monkeypatch.setattr(UserService, "get_current_user", fake_get_current_user)
    monkeypatch.setattr(RatingRepo, "get_by_order_id", fake_get_by_order_id)
    monkeypatch.setattr(RatingService, "submit_report", fake_submit_report)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/orders/1d8e87M/report", json={"reason": "spam"})
    assert response.status_code == 400
    assert response.json()["detail"] == "No review exists to report for this order"


@pytest.mark.asyncio
async def test_feedback_prompt_success(monkeypatch):

    async def fake_check_feedback_prompt(_order_id: str):
        return {
            "order_id": "1d8e87M",
            "prompt_feedback": True,
            "message": "How was your order? Leave a rating and review!",
        }

    monkeypatch.setattr(
        RatingService, "check_feedback_prompt", fake_check_feedback_prompt
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/orders/1d8e87M/feedback-prompt")
    assert response.status_code == 200
    assert response.json() == {
        "order_id": "1d8e87M",
        "prompt_feedback": True,
        "message": "How was your order? Leave a rating and review!",
    }


@pytest.mark.asyncio
async def test_feedback_prompt_order_not_found(monkeypatch):

    async def fake_check_feedback_prompt(_order_id: str):
        raise ValueError("Order not found")

    monkeypatch.setattr(
        RatingService, "check_feedback_prompt", fake_check_feedback_prompt
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/orders/FAKE_ID/feedback-prompt")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_filter_reviews_success(monkeypatch):

    async def fake_get_filtered_reviews(_restaurant_id: int, stars: int | None = None):
        assert stars is None
        return {
            "restaurant_id": 16,
            "stars_filter": None,
            "total_reviews": 2,
            "reviews": [
                {"order_id": "abc123", "submitted_stars": 5, "review_text": "Amazing!"},
                {"order_id": "def456", "submitted_stars": 3, "review_text": "Okay"},
            ],
        }

    monkeypatch.setattr(
        RatingService, "get_filtered_reviews", fake_get_filtered_reviews
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/orders/restaurants/16/reviews")
    assert response.status_code == 200
    assert response.json()["restaurant_id"] == 16
    assert response.json()["total_reviews"] == 2


@pytest.mark.asyncio
async def test_filter_reviews_by_stars(monkeypatch):

    async def fake_get_filtered_reviews(_restaurant_id: int, stars: int | None = None):
        assert stars == 5
        return {
            "restaurant_id": 16,
            "stars_filter": 5,
            "total_reviews": 1,
            "reviews": [
                {"order_id": "abc123", "submitted_stars": 5, "review_text": "Amazing!"}
            ],
        }

    monkeypatch.setattr(
        RatingService, "get_filtered_reviews", fake_get_filtered_reviews
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/orders/restaurants/16/reviews?stars=5")
    assert response.status_code == 200
    assert response.json()["stars_filter"] == 5
    assert response.json()["total_reviews"] == 1


@pytest.mark.asyncio
async def test_filter_reviews_restaurant_not_found(monkeypatch):

    async def fake_get_filtered_reviews(_restaurant_id: int, stars: int | None = None):
        raise ValueError("Restaurant not found")

    monkeypatch.setattr(
        RatingService, "get_filtered_reviews", fake_get_filtered_reviews
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/orders/restaurants/9999/reviews")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"
