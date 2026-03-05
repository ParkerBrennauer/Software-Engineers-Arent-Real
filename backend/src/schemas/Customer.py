"""Customer schema class module."""

from pydantic import BaseModel


class Customer(BaseModel):

    name: str
    login: str
    password: str
    email: str
    paymentType: str
    paymentdetails: str
    pastorders: list


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
