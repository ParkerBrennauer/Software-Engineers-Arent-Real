from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_current_user
from src.schemas.discount_schema import DiscountCreate, DiscountApply
from src.services.discount_services import DiscountServices

router = APIRouter(prefix="/discounts", tags=["discounts"])


def get_current_owner(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "owner":
        raise HTTPException(
            status_code=403,
            detail="Only restaurant owners can perform this action",
        )
    return current_user


@router.post("/apply")
async def apply_discount(payload: DiscountApply):
    result = await DiscountServices.applyDiscount(payload.order_total, payload.discount_code)

    if result is None:
        raise HTTPException(status_code=404, detail="Discount not found")

    return {"discounted_total": result}


@router.post("/")
async def create_discount(
    payload: DiscountCreate,
    current_user: dict = Depends(get_current_owner),
):
    if current_user.get("restaurant_id") != payload.restaurant_id:
        raise HTTPException(
            status_code=403,
            detail="You can only manage discounts for your own restaurant",
        )

    result = await DiscountServices.createDiscount(
        payload.discount_rate,
        payload.discount_code,
        payload.restaurant_id,
    )

    if result == "code is invalid":
        raise HTTPException(status_code=400, detail=result)

    return {"message": result}


@router.delete("/{discount_code}")
async def remove_discount(
    discount_code: str,
    current_user: dict = Depends(get_current_owner),
):
    discount = await DiscountServices.get_discount(discount_code)
    if discount is None:
        raise HTTPException(status_code=404, detail="Discount not found")

    if discount.get("restaurant_id") != current_user.get("restaurant_id"):
        raise HTTPException(
            status_code=403,
            detail="You can only manage discounts for your own restaurant",
        )

    result = await DiscountServices.removeDiscount(discount_code)

    if result == "Discount not found":
        raise HTTPException(status_code=404, detail="Discount not found")

    return {"message": result}