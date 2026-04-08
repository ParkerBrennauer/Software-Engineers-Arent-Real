import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_rate_order_success(client, monkeypatch):
    order_id = "order1"
    username = "customer1"
    payload = {"stars": 5}

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
            "cost": 25.00,
            "submitted_stars": None,
            "review_text": None,
        }

    async def fake_submit_rating(_order_id: str, _payload):
        from src.schemas.rating_schema import RatingResponse

        return RatingResponse(order_id=_order_id, stars=_payload.stars)

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingService.submit_rating",
        fake_submit_rating,
    )

    response = client.post(f"/orders/{order_id}/rating", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["order_id"] == order_id
    assert data["stars"] == 5


@pytest.mark.asyncio
async def test_rate_order_not_logged_in(client, monkeypatch):
    order_id = "order1"
    payload = {"stars": 5}

    def fake_get_current_user():
        return None

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )

    response = client.post(f"/orders/{order_id}/rating", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No user currently logged in" in response.json()["detail"]


@pytest.mark.asyncio
async def test_rate_order_permission_denied(client, monkeypatch):
    order_id = "order1"
    username = "customer2"
    payload = {"stars": 5}

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
            "cost": 25.00,
        }

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )

    response = client.post(f"/orders/{order_id}/rating", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "does not have permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_rate_order_not_found(client, monkeypatch):
    order_id = "nonexistent"
    username = "customer1"
    payload = {"stars": 5}

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return None

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )

    response = client.post(f"/orders/{order_id}/rating", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Order not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_submit_review_success(client, monkeypatch):
    order_id = "order1"
    username = "customer1"
    payload = {"review_text": "Great pizza!"}

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
            "submitted_stars": 5,
            "review_text": None,
        }

    async def fake_submit_review(_order_id: str, _payload):
        from src.schemas.review_schema import ReviewResponse

        return ReviewResponse(
            order_id=_order_id,
            restaurant_id=1,
            review_text=_payload.review_text,
        )

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingService.submit_review",
        fake_submit_review,
    )

    response = client.post(f"/orders/{order_id}/review", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["order_id"] == order_id
    assert data["review_text"] == "Great pizza!"


@pytest.mark.asyncio
async def test_submit_review_permission_denied(client, monkeypatch):
    order_id = "order1"
    username = "customer2"
    payload = {"review_text": "Great pizza!"}

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
        }

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )

    response = client.post(f"/orders/{order_id}/review", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "does not have permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_edit_review_success(client, monkeypatch):
    order_id = "order1"
    username = "customer1"
    payload = {"stars": 4, "review_text": "Pretty good pizza"}

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
            "submitted_stars": 5,
            "review_text": "Good pizza",
        }

    async def fake_edit_order_review(_order_id: str, _payload):
        from src.schemas.review_schema import ReviewEditResponse

        return ReviewEditResponse(
            order_id=_order_id,
            submitted_stars=_payload.stars or 5,
            review_text=_payload.review_text or "Good pizza",
        )

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingService.edit_order_review",
        fake_edit_order_review,
    )

    response = client.put(f"/orders/{order_id}/review", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["order_id"] == order_id


@pytest.mark.asyncio
async def test_edit_review_permission_denied(client, monkeypatch):
    order_id = "order1"
    username = "customer2"
    payload = {"stars": 4}

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
            "submitted_stars": 5,
        }

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )

    response = client.put(f"/orders/{order_id}/review", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "does not have permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_review_success(client, monkeypatch):
    order_id = "order1"
    username = "customer1"

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
            "submitted_stars": 5,
            "review_text": "Good pizza",
        }

    async def fake_delete_order_review(_order_id: str):
        from src.schemas.review_schema import DeleteResponse

        return DeleteResponse(
            order_id=_order_id, message="Review and rating deleted successfully"
        )

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingService.delete_order_review",
        fake_delete_order_review,
    )

    response = client.delete(f"/orders/{order_id}/review")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["order_id"] == order_id
    assert "deleted successfully" in data["message"]


@pytest.mark.asyncio
async def test_delete_review_permission_denied(client, monkeypatch):
    order_id = "order1"
    username = "customer2"

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
            "submitted_stars": 5,
        }

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )

    response = client.delete(f"/orders/{order_id}/review")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "does not have permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_report_review_success(client, monkeypatch):
    order_id = "order1"
    username = "customer1"
    payload = {"reason": "spam", "description": "Spam review"}

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
            "submitted_stars": 5,
            "review_text": "Good pizza",
        }

    async def fake_submit_report(_order_id: str, _payload):
        from src.schemas.review_schema import ReportResponse

        return ReportResponse(
            report_id=1,
            order_id=_order_id,
            reason=_payload.reason,
            description=_payload.description,
            message="Report submitted"
        )

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingService.submit_report",
        fake_submit_report,
    )

    response = client.post(f"/orders/{order_id}/report", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["order_id"] == order_id


@pytest.mark.asyncio
async def test_report_review_permission_denied(client, monkeypatch):
    order_id = "order1"
    username = "customer2"
    payload = {"reason": "spam", "description": "Spam review"}

    def fake_get_current_user():
        return username

    async def fake_get_by_order_id(_order_id: str):
        return {
            "id": "order1",
            "customer": "customer1",
            "restaurant": "Pizza Place",
        }

    monkeypatch.setattr(
        "src.api.routers.rating_router.UserService.get_current_user",
        fake_get_current_user,
    )
    monkeypatch.setattr(
        "src.api.routers.rating_router.RatingRepo.get_by_order_id",
        fake_get_by_order_id,
    )

    response = client.post(f"/orders/{order_id}/report", json=payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "does not have permission" in response.json()["detail"]
