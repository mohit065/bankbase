from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    id: int
    role: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
