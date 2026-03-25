from fastapi import APIRouter, HTTPException, status
from src.schemas.item_schema import ItemUpdate, ItemUpdateAnalytics, ItemCreate
from src.services.item_services import ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/{item_key}", status_code=status.HTTP_200_OK)
async def get_item_by_key(item_key: str):
    item = await ItemService.get_items_by_key(item_key)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return item


@router.get("/restaurant/{restaurant_id}", status_code=status.HTTP_200_OK)
async def get_items_by_restaurant_id(restaurant_id: int):
    items = await ItemService.get_items_by_restaurant_id(restaurant_id)
    return items


@router.patch("/{item_key}", status_code=status.HTTP_200_OK)
async def update_item(item_key: str, item_in: ItemUpdate):
    try:
        updated_item = await ItemService.update_item_by_key(item_key, item_in)
        return updated_item
    except ValueError as err:
        message = str(err)
        if message == "Item does not exist":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=message
            ) from err
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=message
        ) from err


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_item(item_in: ItemCreate):
    try:
        return await ItemService.create_item(item_in)
    except ValueError as err:
        message = str(err)

        status_code = status.HTTP_400_BAD_REQUEST
        if message == "Item already exists":
            status_code = status.HTTP_409_CONFLICT

        raise HTTPException(status_code=status_code, detail=message) from err
