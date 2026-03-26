import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.fixture
def test_customer():
    customer_data = {
        "username": "test_customer",
        "password": "password123",
        "role": "customer",
        "email": "test@test.com",
        "name": "test_customer_name",
        "payment_type": "credit card",
        "payment_details": "1234567812345678"
    }
    response = client.post("/users/register/customer", json=customer_data)
    assert response.status_code in [200, 201]
    return customer_data

def test_create_order_success(test_customer):
    order_data = {
        "restaurant": "Test Restaurant",
        "customer": test_customer["username"],
        "time": 30,
        "cuisine": "testfood",
        "distance": 2.0,
        "items": [
            {"id": 1, "price": 10.0},
            {"id": 2, "price": 5.0}
        ]
    }

    response = client.post("/orders/", json=order_data)

    assert response.status_code == 200
    data = response.json()

    assert data["restaurant"] == "Test Restaurant"
    assert data["customer"] == "test_customer"
    assert data["order_status"] == "payment pending"
    assert data["payment_status"] == "pending"
    assert data["locked"] is False

def test_get_order_success(test_customer):
    order_data = {
        "restaurant": "Test Restaurant",
        "customer": test_customer["username"],
        "time": 30,
        "cuisine": "testfood",
        "distance": 2.0,
        "items": [
            {"id": 1, "price": 10.0}
        ]
    }

    create_response = client.post("/orders/", json=order_data)
    created_order = create_response.json()

    order_id = created_order["id"]

    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["restaurant"] == "Test Restaurant"

def test_update_order_success(test_customer):
    order_data = {
        "restaurant": "Test Restaurant",
        "customer": test_customer["username"],
        "time": 30,
        "cuisine": "testfood",
        "distance": 2.0,
        "items": [
            {"id": 1, "price": 10.0}
        ]
    }

    create_response = client.post("/orders/", json=order_data)
    created_order = create_response.json()
    order_id = created_order["id"]

    update_data = {
        "restaurant": "Updated Restaurant",
        "items": [
            {"id": 1, "price": 20.0}
        ]
    }

    response = client.put(f"/orders/{order_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["restaurant"] == "Updated Restaurant"
    assert data["cost"] == 22.6

def test_lock_order_success(test_customer):
    order_data = {
        "restaurant": "Test Restaurant",
        "customer": test_customer["username"],
        "time": 30,
        "cuisine": "testfood",
        "distance": 2.0,
        "items": [
            {"id": 1, "price": 10.0}
        ]
    }

    create_response = client.post("/orders/", json=order_data)
    created_order = create_response.json()
    order_id = created_order["id"]

    response = client.patch(f"/orders/{order_id}/lock")

    assert response.status_code == 200
    data = response.json()
    assert data["locked"] is True

def test_get_order_not_found(test_customer):
    response = client.get("/orders/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"

def test_update_locked_order_fails(test_customer):
    order_data = {
        "restaurant": "Test Restaurant",
        "customer": test_customer["username"],
        "time": 30,
        "cuisine": "testfood",
        "distance": 2.0,
        "items": [
            {"id": 1, "price": 10.0}
        ]
    }

    create_response = client.post("/orders/", json=order_data)
    created_order = create_response.json()
    order_id = created_order["id"]

    client.patch(f"/orders/{order_id}/lock")

    response = client.put(
        f"/orders/{order_id}",
        json={"restaurant": "Should Fail"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Order is locked and cannot be updated"