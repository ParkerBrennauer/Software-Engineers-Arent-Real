from fastapi import APIRouter, HTTPException
from src.services.tips_service import TipService
from src.services.driver_service import DriverService
from src.schemas.tip_schema import TipRequest

router = APIRouter(prefix="/orders", tags=["Tips"])

@router.post("/{order_id}/tip")
async def apply_tip(order_id: int, tip: TipRequest):
    try:
        result = await TipService.apply_tip(
            order_id,
            tip_percent=tip.tip_percent,
            tip_amount=tip.tip_amount
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/tip/payout")
async def payout_tip(order_id: int):
    try:
        result = await DriverService.tip_driver(order_id)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
