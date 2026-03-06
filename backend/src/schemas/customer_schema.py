from pydantic import BaseModel, field_validator


class Customer(BaseModel):

    name: str
    login: str
    password: str
    email: str
    paymentType: str
    paymentdetails: str
    pastorders: list

    # Validating customer's payment details
    @field_validator("paymentdetails")
    @classmethod
    def validate_card_number(cls, value):

        if not value.isdigit():
            raise ValueError("Card number must contain only digits.")
        if len(value) not in [15, 16]:
            raise ValueError("Card number must be 15 or 16 digits.")

        return value

    # Validating customer's payment type
    @field_validator("paymentType")
    @classmethod
    def validate_payment_type(cls, value):

        if value.lower() not in ["credit card", "debit card"]:
            raise ValueError("Payment type must be either credit card or debit card.")

        return value

class CreateCustomer(BaseModel):

    name: str
    login: str
    password: str
    email: str
    paymentType: str
    paymentdetails: str


class UpdateCustomer(BaseModel):

    name: str
    login: str
    password: str
    email: str
    paymentType: str
    paymentdetails: str
    pastorders: list
