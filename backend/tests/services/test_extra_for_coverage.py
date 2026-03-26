from unittest import result

import pytest
from unittest.mock import AsyncMock, patch
from src.services.order_services import OrderService
from src.services.payment_service import PaymentService
from src.services.item_services import ItemService
from src.services.rating_service import RatingService
from src.schemas.order_schema import Order, OrderCreate, PaymentStatus, OrderStatus
from src.schemas.item_schema import ItemCreate, ItemUpdate
from src.schemas.rating_schema import RatingCreate
from src.schemas.review_schema import ReviewCreate, ReviewEdit


@pytest.mark.asyncio
@patch(
    "src.repositories.order_repo.OrderRepo.get_largest_order_id", new_callable=AsyncMock
)
@patch("src.repositories.order_repo.OrderRepo.save_order", new_callable=AsyncMock)
async def test_create_order_with_no_existing_orders(mock_save, mock_get_largest):
    mock_get_largest.return_value = None
    mock_save.return_value = {
        "id": 1,
        "items": [{"id": 1, "price": 10.0}],
        "cost": 11.3,
        "order_status": "payment pending",
        "payment_status": "pending",
        "locked": False,
    }

    order_create = OrderCreate(
        items=[{"id": 1, "price": 10.0}],
        cost=10.0,
        restaurant="Test",
        customer="test_user",
        time=30,
        cuisine="Italian",
        distance=2.0,
    )

    result = await OrderService.create_order(order_create)
    assert result.id == 1
    mock_get_largest.assert_called_once()
    mock_save.assert_called_once()


@pytest.mark.asyncio
@patch("src.repositories.order_repo.OrderRepo.get_order", new_callable=AsyncMock)
async def test_calculate_order_cost_with_non_dict_items(mock_get_order):
    items = ["invalid", {"price": 10.0}, 5, {"price": 20.0}]

    cost = await OrderService.calculate_order_cost(items)

    assert cost == 33.9


@pytest.mark.asyncio
@patch("src.repositories.order_repo.OrderRepo.get_order", new_callable=AsyncMock)
async def test_calculate_order_cost_empty_list(mock_get_order):
    cost = await OrderService.calculate_order_cost([])
    assert cost == 0.0


@pytest.mark.asyncio
@patch("src.repositories.order_repo.OrderRepo.get_order", new_callable=AsyncMock)
@patch("src.repositories.order_repo.OrderRepo.update_order", new_callable=AsyncMock)
async def test_update_order_with_non_existent_order(mock_update, mock_get):
    mock_get.return_value = None

    with pytest.raises(ValueError, match="Order not found"):
        await OrderService.update_order(999, {"restaurant": "New"})


@pytest.mark.asyncio
@patch("src.repositories.order_repo.OrderRepo.get_order", new_callable=AsyncMock)
async def test_update_order_when_locked(mock_get):
    mock_get.return_value = {"id": 1, "locked": True, "restaurant": "Original"}

    with pytest.raises(ValueError, match="Order is locked"):
        await OrderService.update_order(1, {"restaurant": "New"})


@pytest.mark.asyncio
@patch("src.repositories.order_repo.OrderRepo.get_order", new_callable=AsyncMock)
@patch("src.repositories.order_repo.OrderRepo.update_order", new_callable=AsyncMock)
async def test_lock_already_locked_order(mock_update, mock_get):
    mock_get.return_value = {
        "id": 1,
        "locked": True,
        "order_status": "pending",
        "payment_status": "unpaid",
        "items": [],
        "cost": 0,
    }

    result = await OrderService.lock_order(1)
    assert result.locked is True
    # update_order should not be called since order is already locked
    mock_update.assert_not_called()


@pytest.mark.asyncio
@patch("src.repositories.order_repo.OrderRepo.get_order", new_callable=AsyncMock)
async def test_get_order_status_non_existent(mock_get):
    mock_get.return_value = None

    with pytest.raises(ValueError, match="Order not found"):
        await OrderService.get_order_status(999)


@pytest.mark.asyncio
@patch("src.services.order_services.OrderService.update_order", new_callable=AsyncMock)
async def test_cancel_order(mock_update):
    mock_update.return_value = {"id": 1, "order_status": "cancelled"}

    await OrderService.cancel_order(1)

    mock_update.assert_called_once_with(1, {"order_status": "cancelled"})


@pytest.mark.asyncio
@patch("src.services.order_services.OrderService.update_order", new_callable=AsyncMock)
async def test_mark_ready_for_pickup(mock_update):
    mock_update.return_value = {"id": 1, "order_status": "ready_for_pickup"}

    await OrderService.mark_ready_for_pickup(1)

    mock_update.assert_called_once_with(1, {"order_status": "ready_for_pickup"})


@pytest.mark.asyncio
@patch("src.services.order_services.OrderService.update_order", new_callable=AsyncMock)
async def test_assign_driver(mock_update):
    mock_update.return_value = {"id": 1, "driver": "driver_001"}

    await OrderService.assign_driver(1, "driver_001")

    mock_update.assert_called_once_with(1, {"driver": "driver_001"})


@pytest.mark.asyncio
async def test_process_payment_success():
    order = Order(
        items=[{"id": 1, "price": 10.0}],
        cost=11.3,
        restaurant="Test",
        customer="test_user",
        time=30,
        cuisine="Italian",
        distance=2.0,
        payment_status=PaymentStatus.PENDING,
    )

    result = await PaymentService.process_payment(order)

    assert result.payment_status == PaymentStatus.ACCEPTED
    assert result.order_status == OrderStatus.CONFIRMED


@pytest.mark.asyncio
async def test_process_payment_already_accepted():
    order = Order(
        items=[{"id": 1, "price": 10.0}],
        cost=11.3,
        restaurant="Test",
        customer="test_user",
        time=30,
        cuisine="Italian",
        distance=2.0,
        payment_status=PaymentStatus.ACCEPTED,
    )

    with pytest.raises(ValueError, match="Payment already successfully processed"):
        await PaymentService.process_payment(order)


@pytest.mark.asyncio
@patch("src.repositories.item_repo.ItemRepo.get_by_key", new_callable=AsyncMock)
async def test_get_items_by_key(mock_get):
    mock_get.return_value = [{"item_name": "Burger", "price": 9.99}]

    result = await ItemService.get_items_by_key("Burger_1")

    assert len(result) == 1
    assert result[0]["item_name"] == "Burger"


@pytest.mark.asyncio
@patch(
    "src.repositories.item_repo.ItemRepo.get_by_restaurant_id", new_callable=AsyncMock
)
async def test_get_items_by_restaurant_id(mock_get):
    mock_get.return_value = [
        {"item_name": "Burger", "price": 9.99},
        {"item_name": "Pizza", "price": 12.99},
    ]

    result = await ItemService.get_items_by_restaurant_id(1)

    assert len(result) == 2


@pytest.mark.asyncio
@patch("src.repositories.item_repo.ItemRepo.update_by_key", new_callable=AsyncMock)
async def test_update_item_success(mock_update):
    mock_update.return_value = {"item_name": "Burger", "price": 10.99}

    update = ItemUpdate(price=10.99)
    result = await ItemService.update_item_by_key("Burger_1", update)

    assert result["price"] == 10.99


@pytest.mark.asyncio
@patch("src.repositories.item_repo.ItemRepo.update_by_key", new_callable=AsyncMock)
async def test_update_nonexistent_item(mock_update):
    mock_update.return_value = None

    update = ItemUpdate(price=10.99)

    with pytest.raises(ValueError, match="Item does not exist"):
        await ItemService.update_item_by_key("NonExistent_1", update)


@pytest.mark.asyncio
@patch("src.repositories.item_repo.ItemRepo.get_by_key", new_callable=AsyncMock)
@patch("src.repositories.item_repo.ItemRepo.save_item", new_callable=AsyncMock)
async def test_create_item_success(mock_save, mock_get):
    mock_get.return_value = None
    mock_save.return_value = {"item_name": "Burger", "restaurant_id": 1}

    item_create = ItemCreate(
        item_name="Burger",
        restaurant_id=1,
        price=9.99,
        description="Classic burger",
        cost=9.99,
        cuisine="American",
    )

    result = await ItemService.create_item(item_create)

    assert result["item_name"] == "Burger"
    mock_save.assert_called_once()


@pytest.mark.asyncio
@patch("src.repositories.item_repo.ItemRepo.get_by_key", new_callable=AsyncMock)
async def test_create_item_already_exists(mock_get):
    mock_get.return_value = {"item_name": "Burger", "restaurant_id": 1}

    item_create = ItemCreate(
        item_name="Burger",
        restaurant_id=1,
        price=9.99,
        description="Classic burger",
        cost=9.99,
        cuisine="American",
    )

    with pytest.raises(ValueError, match="Item already exists"):
        await ItemService.create_item(item_create)


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
@patch(
    "src.repositories.rating_repo.RatingRepo.update_submitted_rating",
    new_callable=AsyncMock,
)
async def test_submit_rating_success(mock_update, mock_get):
    mock_get.return_value = {"id": "order_1", "submitted_stars": None}
    mock_update.return_value = {"id": "order_1", "submitted_stars": 5}

    rating = RatingCreate(stars=5)
    result = await RatingService.submit_rating("order_1", rating)

    assert result.stars == 5
    assert result.order_id == "order_1"


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
async def test_submit_rating_order_not_found(mock_get):
    mock_get.return_value = None

    rating = RatingCreate(stars=5)

    with pytest.raises(ValueError, match="Order not found"):
        await RatingService.submit_rating("nonexistent", rating)


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
async def test_submit_rating_already_rated(mock_get):
    mock_get.return_value = {"id": "order_1", "submitted_stars": 4}

    rating = RatingCreate(stars=5)

    with pytest.raises(ValueError, match="already been rated"):
        await RatingService.submit_rating("order_1", rating)


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
@patch(
    "src.repositories.rating_repo.RatingRepo.update_submitted_rating",
    new_callable=AsyncMock,
)
async def test_submit_rating_update_fails(mock_update, mock_get):
    mock_get.return_value = {"id": "order_1", "submitted_stars": None}
    mock_update.return_value = None

    rating = RatingCreate(stars=5)

    with pytest.raises(ValueError, match="Order not found"):
        await RatingService.submit_rating("order_1", rating)


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
@patch(
    "src.repositories.rating_repo.RatingRepo.get_restaurant_id_by_order_id",
    new_callable=AsyncMock,
)
@patch(
    "src.repositories.rating_repo.RatingRepo.update_review_text", new_callable=AsyncMock
)
async def test_submit_review_success(mock_update, mock_get_restaurant, mock_get_order):
    mock_get_order.return_value = {"id": "order_1", "review_text": None}
    mock_get_restaurant.return_value = 5
    mock_update.return_value = {"id": "order_1", "review_text": "Great food!"}

    review = ReviewCreate(review_text="Great food!")
    result = await RatingService.submit_review("order_1", review)

    assert result.review_text == "Great food!"
    assert result.restaurant_id == 5


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
async def test_submit_review_order_not_found(mock_get):
    mock_get.return_value = None

    review = ReviewCreate(review_text="Great!")

    with pytest.raises(ValueError, match="Order not found"):
        await RatingService.submit_review("nonexistent", review)


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
async def test_submit_review_already_reviewed(mock_get):
    mock_get.return_value = {"id": "order_1", "review_text": "Already reviewed"}

    review = ReviewCreate(review_text="New review")

    with pytest.raises(ValueError, match="already been reviewed"):
        await RatingService.submit_review("order_1", review)


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
async def test_submit_review_restaurant_not_found(mock_get):
    mock_get.return_value = {"id": "order_1", "review_text": None}

    with patch(
        "src.repositories.rating_repo.RatingRepo.get_restaurant_id_by_order_id",
        new_callable=AsyncMock,
    ) as mock_get_rest:
        mock_get_rest.return_value = None

        review = ReviewCreate(review_text="Great!")

        with pytest.raises(ValueError, match="Restaurant not found"):
            await RatingService.submit_review("order_1", review)


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
@patch(
    "src.repositories.rating_repo.RatingRepo.update_review_fields",
    new_callable=AsyncMock,
)
async def test_edit_review_success(mock_update, mock_get):
    mock_get.return_value = {
        "id": "order_1",
        "submitted_stars": 4,
        "review_text": "Good",
    }
    mock_update.return_value = {
        "id": "order_1",
        "submitted_stars": 5,
        "review_text": "Excellent!",
    }

    edit = ReviewEdit(stars=5, review_text="Excellent!")
    result = await RatingService.edit_order_review("order_1", edit)

    assert result.submitted_stars == 5
    assert result.review_text == "Excellent!"


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
async def test_edit_review_no_review_exists(mock_get):
    mock_get.return_value = {
        "id": "order_1",
        "submitted_stars": None,
        "review_text": None,
    }

    edit = ReviewEdit(stars=5)

    with pytest.raises(ValueError, match="No review exists"):
        await RatingService.edit_order_review("order_1", edit)


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
async def test_edit_review_nothing_to_update(mock_get):
    mock_get.return_value = {
        "id": "order_1",
        "submitted_stars": 4,
        "review_text": "Good",
    }

    edit = ReviewEdit(stars=None, review_text=None)

    with pytest.raises(ValueError, match="Nothing to update"):
        await RatingService.edit_order_review("order_1", edit)


@pytest.mark.asyncio
@patch(
    "src.repositories.rating_repo.RatingRepo.get_by_order_id", new_callable=AsyncMock
)
@patch(
    "src.repositories.rating_repo.RatingRepo.update_review_fields",
    new_callable=AsyncMock,
)
async def test_edit_review_update_fails(mock_update, mock_get):
    mock_get.return_value = {
        "id": "order_1",
        "submitted_stars": 4,
        "review_text": "Good",
    }
    mock_update.return_value = None

    edit = ReviewEdit(stars=5)

    with pytest.raises(ValueError, match="Order not found"):
        await RatingService.edit_order_review("order_1", edit)
