from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    password: str
    role: Optional[str] = "clerk"

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

class Employee(EmployeeBase):
    id: int
    role: str
    joined_on: datetime
    model_config = ConfigDict(from_attributes=True)
