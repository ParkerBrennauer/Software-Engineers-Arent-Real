from pydantic import BaseModel, EmailStr
from enum import Enum
  
class UserRole(str, Enum):
  CUSTOMER = "customer"
  DRIVER = "driver"
  RESTAURANT_OWNER = "owner"
  RESTAURANT_STAFF = "staff"

class UserBase(BaseModel):
  email: EmailStr
  full_name: str
  role: UserRole
  username: str

class UserRegister(UserBase):
  password: str

class UserLogin(BaseModel):
  username: str
  password: str

class UserResponse(BaseModel):
  id: int
  requires_2fa: bool = False
  