# Testing Coverage — Feature 9: FR1 (Star-Based Rating System)

## Overview

This document describes the unit and integration tests for FR1 for Feature 9, which allows customers to rate completed orders using a star-based rating system (1–5 stars).

**Acceptance Criteria:**
- A customer can submit a star rating between 1 and 5 for a completed order
- The system prevents duplicate ratings on the same order
- The system returns appropriate errors for invalid orders

---

## Files Under Test

| File | Layer | Key Functions/Classes |
|------|-------|-----------------------|
| `services/rating_service.py` | Service | `submit_rating(order_id, payload)` |
| `repositories/deliveries_repo.py` | Data | `get_order(order_id)`, `update_rating(order_id, stars)` |
| `schemas/ratings.py` | Schema | `RatingCreate`, `RatingResponse` |
| `routers/ratings.py` | Router | `POST /orders/{order_id}/rating` |

---

## Unit Tests (`tests/test_unit_rating.py`)

Unit tests verify individual functions in **isolation** using mocked dependencies. 

### Test 1: `test_submit_rating_success`
- **Function tested:** `submit_rating()` in `rating_service.py`
- **What it checks:** When given a valid order that has not been rated yet (`submitted_stars` is `None`), the function returns the correct `order_id` and `stars`.
- **How:** Mocks `get_order` to return a fake unrated order, mocks `update_rating` to simulate saving. Asserts the return dict matches expected values.

### Test 2: `test_submit_rating_order_not_found`
- **Function tested:** `submit_rating()` in `rating_service.py`
- **What it checks:** When the order does not exist (`get_order` returns `None`), the function raises an `HTTPException` with status code 404.
- **How:** Mocks `get_order` to return `None`. Uses `pytest.raises` to catch the exception and assert the status code and detail message.

### Test 3: `test_submit_rating_already_rated`
- **Function tested:** `submit_rating()` in `rating_service.py`
- **What it checks:** When the order has already been rated (`submitted_stars` is not `None`), the function raises an `HTTPException` with status code 400.
- **How:** Mocks `get_order` to return an order with `submitted_stars: 4`. Asserts the correct exception is raised.

### Test 4: `test_rating_schema_rejects_zero_stars` / `test_rating_schema_rejects_six_stars` / `test_rating_schema_accepts_valid_stars`
- **Class tested:** `RatingCreate` in `schemas/ratings.py`
- **What it checks:** The Pydantic schema enforces the 1–5 star constraint. Stars of 0 or 6 raise `ValidationError`. Stars 1 through 5 are accepted.
- **How:** Directly instantiates `RatingCreate` with boundary values and asserts validation behavior.

---

## Integration Tests (`tests/test_integration_rating.py`)

Integration tests verify the **full request flow** through the API: HTTP Request → Router → Service → Repository → JSON Response. Uses FastAPI's `TestClient`.

### Test 1: `test_rate_order_success`
- **Endpoint:** `POST /orders/1d8e87M/rating` with `{"stars": 5}`
- **What it checks:** A valid rating request returns 200 with the correct response body, and the rating is persisted to `reviews.json`.
- **How:** Sends a POST via TestClient, asserts status 200 and response JSON, then reads the JSON file to verify persistence.

### Test 2: `test_rate_nonexistent_order`
- **Endpoint:** `POST /orders/NONEXISTENT_ORDER/rating`
- **What it checks:** Rating a nonexistent order returns 404 with the correct error detail.

### Test 3: `test_rate_order_duplicate`
- **Endpoint:** `POST /orders/f4d84dC/rating` (called twice)
- **What it checks:** First rating succeeds (200), second rating on the same order is rejected (400).

### Test 4: `test_rate_order_invalid_stars_zero` / `test_rate_order_invalid_stars_six`
- **Endpoint:** `POST /orders/1d8e87M/rating` with `{"stars": 0}` and `{"stars": 6}`
- **What it checks:** Invalid star values are rejected by Pydantic validation, returning 422 Unprocessable Entity.

---

## CI Pipeline

Tests run automatically via GitHub Actions on every pull request (see `.github/workflows/pytest.yml`). The pipeline:

1. Checks out the code
2. Installs Python 3.11 and project dependencies
3. Runs `pytest tests/ -v` from inside `src/`
4. PR is blocked from merging if any test fails

Style checking is handled separately by the existing `pylint.yml` workflow.

---

## How to Run Tests Locally

```bash
cd Software-Engineering/backend/src
pip install pytest httpx
pytest tests/ -v
```