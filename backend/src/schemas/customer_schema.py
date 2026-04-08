from pydantic import field_validator
from src.schemas.user_schema import UserRegister, UserUpdate, UserRole
from src.schemas.item_schema import ItemBase

class CustomerRegister(UserRegister):
    role: UserRole = UserRole.CUSTOMER
    payment_type: str
    payment_details: str

    @field_validator('payment_details')
    @classmethod
    def validate_card_number(cls, value):
        if not value.isdigit():
            raise ValueError('Card number must contain only digits.')
        if len(value) not in [15, 16]:
            raise ValueError('Card number must be 15 or 16 digits.')
        return value

    @field_validator('payment_type')
    @classmethod
    def validate_payment_type(cls, value):
        if value.lower() not in ['credit card', 'debit card']:
            raise ValueError('Payment type must be either credit card or debit card.')
        return value

class CustomerUpdate(UserUpdate):
    payment_type: str | None = None
    payment_details: str | None = None

    @field_validator('payment_details')
    @classmethod
    def validate_card_number(cls, value):
        if value is None:
            return value
        if not value.isdigit():
            raise ValueError('Card number must contain only digits.')
        if len(value) not in [15, 16]:
            raise ValueError('Card number must be 15 or 16 digits.')
        return value

    @field_validator('payment_type')
    @classmethod
    def validate_payment_type(cls, value):
        if value is None:
            return value
        if value.lower() not in ['credit card', 'debit card']:
            raise ValueError('Payment type must be either credit card or debit card.')
        return value
