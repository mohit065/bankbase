from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class AccountBase(BaseModel):
    PID: str
    name: str
    email: EmailStr
    phone: Optional[str] = None


class AccountCreate(AccountBase):
    balance: float = 0.0


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    PID: Optional[str] = None
    balance: Optional[float] = None
    is_active: Optional[bool] = None


class Account(AccountBase):
    id: int
    balance: float
    created_on: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
