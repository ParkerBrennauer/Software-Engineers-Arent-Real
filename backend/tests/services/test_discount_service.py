import pytest
from unittest.mock import AsyncMock, patch
from src.services.discount_services import DiscountServices


@pytest.mark.asyncio
@patch("src.services.discount_services.DiscountRepo.find_savings", new_callable=AsyncMock)
async def test_apply_discount_success(mock_find_savings):
    mock_find_savings.return_value = 0.80

    result = await DiscountServices.applyDiscount(100.0, "SAVE20")

    assert result == 80.0
    mock_find_savings.assert_awaited_once_with("SAVE20")


@pytest.mark.asyncio
@patch("src.services.discount_services.DiscountRepo.find_savings", new_callable=AsyncMock)
async def test_apply_discount_rounding(mock_find_savings):
    mock_find_savings.return_value = 0.3333

    result = await DiscountServices.applyDiscount(100.0, "SAVE67")

    assert result == 33.33
    mock_find_savings.assert_awaited_once_with("SAVE67")


@pytest.mark.asyncio
@patch("src.services.discount_services.DiscountRepo.check_real", new_callable=AsyncMock)
@patch("src.services.discount_services.DiscountRepo.save_code", new_callable=AsyncMock)
async def test_create_discount_success(mock_save_code, mock_check_real):
    mock_check_real.return_value = True
    mock_save_code.return_value = {
        "SAVE10": {
            "restaurant_id": 1,
            "discount_rate": 0.10
        }
    }

    result = await DiscountServices.createDiscount(0.10, "SAVE10", 1)

    assert result == "valid code, enjoy saving"
    mock_save_code.assert_awaited_once_with({
        "SAVE10": {
            "restaurant_id": 1,
            "discount_rate": 0.10
        }
    })
    mock_check_real.assert_awaited_once_with("SAVE10")


@pytest.mark.asyncio
@patch("src.services.discount_services.DiscountRepo.check_real", new_callable=AsyncMock)
@patch("src.services.discount_services.DiscountRepo.save_code", new_callable=AsyncMock)
async def test_create_discount_invalid(mock_save_code, mock_check_real):
    mock_check_real.return_value = False
    mock_save_code.return_value = {
        "SAVE10": {
            "restaurant_id": 1,
            "discount_rate": 0.10
        }
    }

    result = await DiscountServices.createDiscount(0.10, "SAVE10", 1)

    assert result == "code is invalid"
    mock_save_code.assert_awaited_once_with({
        "SAVE10": {
            "restaurant_id": 1,
            "discount_rate": 0.10
        }
    })
    mock_check_real.assert_awaited_once_with("SAVE10")


@pytest.mark.asyncio
@patch("src.services.discount_services.DiscountRepo.remove_code", new_callable=AsyncMock)
async def test_remove_discount_success(mock_remove_code):
    mock_remove_code.return_value = True

    result = await DiscountServices.removeDiscount("SAVE10")

    assert result == "successfully removed code"
    mock_remove_code.assert_awaited_once_with("SAVE10")


@pytest.mark.asyncio
@patch("src.services.discount_services.DiscountRepo.remove_code", new_callable=AsyncMock)
async def test_remove_discount_not_found(mock_remove_code):
    mock_remove_code.return_value = False

    result = await DiscountServices.removeDiscount("SAVE10")

    assert result == "Discount not found"
    mock_remove_code.assert_awaited_once_with("SAVE10")
