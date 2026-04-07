from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@patch("src.api.routers.discount_router.DiscountServices.createDiscount", new_callable=AsyncMock)
def test_create_discount_success(mock_create_discount):
    mock_create_discount.return_value = "valid code, enjoy saving"

    response = client.post(
        "/discounts/",
        json={
            "discount_rate": 0.10,
            "discount_name": "SAVE10",
            "restaurant_id": 1
        }
    )

    assert response.status_code == 200
    assert response.json() == {"message": "valid code, enjoy saving"}
    mock_create_discount.assert_awaited_once_with(0.10, "SAVE10", 1)


@patch("src.api.routers.discount_router.DiscountServices.createDiscount", new_callable=AsyncMock)
def test_create_discount_invalid(mock_create_discount):
    mock_create_discount.return_value = "code is invalid"

    response = client.post(
        "/discounts/",
        json={
            "discount_rate": 0.10,
            "discount_name": "SAVE10",
            "restaurant_id": 1
        }
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "code is invalid"}
    mock_create_discount.assert_awaited_once_with(0.10, "SAVE10", 1)


@patch("src.api.routers.discount_router.DiscountServices.applyDiscount", new_callable=AsyncMock)
def test_apply_discount_success(mock_apply_discount):
    mock_apply_discount.return_value = 80.0

    response = client.post(
        "/discounts/apply",
        json={
            "order_total": 100.0,
            "discount_code": "SAVE20"
        }
    )

    assert response.status_code == 200
    assert response.json() == {"discounted_total": 80.0}
    mock_apply_discount.assert_awaited_once_with(100.0, "SAVE20")


@patch("src.api.routers.discount_router.DiscountServices.applyDiscount", new_callable=AsyncMock)
def test_apply_discount_not_found(mock_apply_discount):
    mock_apply_discount.return_value = None

    response = client.post(
        "/discounts/apply",
        json={
            "order_total": 100.0,
            "discount_code": "BADCODE"
        }
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Discount not found"}
    mock_apply_discount.assert_awaited_once_with(100.0, "BADCODE")


@patch("src.api.routers.discount_router.DiscountServices.removeDiscount", new_callable=AsyncMock)
def test_remove_discount_success(mock_remove_discount):
    mock_remove_discount.return_value = "successfully removed code"

    response = client.delete("/discounts/SAVE10")

    assert response.status_code == 200
    assert response.json() == {"message": "successfully removed code"}
    mock_remove_discount.assert_awaited_once_with("SAVE10")


@patch("src.api.routers.discount_router.DiscountServices.removeDiscount", new_callable=AsyncMock)
def test_remove_discount_not_found(mock_remove_discount):
    mock_remove_discount.return_value = "Discount not found"

    response = client.delete("/discounts/SAVE10")

    assert response.status_code == 404
    assert response.json() == {"detail": "Discount not found"}
    mock_remove_discount.assert_awaited_once_with("SAVE10")