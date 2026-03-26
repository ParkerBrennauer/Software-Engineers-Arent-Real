from fastapi import APIRouter, status
from src.schemas.item_schema import ItemUpdate, ItemCreate
from src.services.item_services import ItemService
from src.api.dependencies import convert_service_error

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/{item_key}", status_code=status.HTTP_200_OK)
async def get_item_by_key(item_key: str):
    try:
        item = await ItemService.get_items_by_key(item_key)
        if not item:
            raise ValueError("Item not found")
        return item
    except ValueError as err:
        raise convert_service_error(err)


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
        raise convert_service_error(err)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_item(item_in: ItemCreate):
    try:
        return await ItemService.create_item(item_in)
    except ValueError as err:
        raise convert_service_error(err)
