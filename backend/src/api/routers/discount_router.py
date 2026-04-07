from fastapi import APIRouter, HTTPException
from src.schemas.discount_schema import DiscountCreate, DiscountApply
from src.services.discount_services import DiscountServices

router = APIRouter(prefix="/discounts", tags=["discounts"])


@router.post("/apply")
async def apply_discount(payload: DiscountApply):
    result = await DiscountServices.applyDiscount(
        payload.order_total,
        payload.discount_code
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Discount not found")

    return {"discounted_total": result}


@router.post("/")
async def create_discount(payload: DiscountCreate):
    result = await DiscountServices.createDiscount(
        payload.discount_rate,
        payload.discount_code,
        payload.restaurant_id
    )

    if result == "code is invalid":
        raise HTTPException(status_code=400, detail=result)

    return {"message": result}


@router.delete("/{discount_code}")
async def remove_discount(discount_code: str):
    result = await DiscountServices.removeDiscount(discount_code)

    if result == "Discount not found":
        raise HTTPException(status_code=404, detail=result)

    return {"message": result}