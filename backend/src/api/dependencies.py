from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from src.api.exceptions import AppException
from src.api.exceptions import ValidationError
from src.api.exceptions import NotFoundError
from src.api.exceptions import ConflictError
from src.api.exceptions import UnauthorizedError
from src.api.exceptions import ForbiddenError
from src.core.utils import get_role_value
from src.repositories.user_repo import UserRepo
from src.services.user_service import UserService

async def get_current_user() -> dict:
    username = UserService.get_current_user()
    if not username:
        raise HTTPException(status_code=401, detail='Not authenticated')
    user = await UserRepo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail='Not authenticated')
    role = get_role_value(user)
    rid = user.get('restaurant_id')
    if rid is not None:
        try:
            rid = int(rid)
        except (TypeError, ValueError):
            rid = None
    return {'id': user['id'], 'role': role, 'restaurant_id': rid}

def setup_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})

def convert_service_error(err: ValueError) -> AppException:
    message = str(err)
    if message in {'User not found', 'Order not found', 'Restaurant not found', 'Restaurant not found for this order', 'Item does not exist', 'Item not found', 'Driver not found', 'Customer not found', 'Owner not found'}:
        return NotFoundError(message)
    if message in {'Username already exists', 'Item already exists', 'Restaurant already exists', 'Restaurant is already in favorites'}:
        return ConflictError(message)
    if 'Invalid username or password' in message:
        return UnauthorizedError(message)
    if message in {'User account is inactive', 'User is not a restaurant owner'} or 'does not have permission' in message:
        return ForbiddenError(message)
    return ValidationError(message)
