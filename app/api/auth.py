from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

from app.db import models 
from app.db.database import get_db
from app.schemas import auth
from app.core import security
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/auth/login", response_model=auth.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.Employee).filter(models.Employee.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"id": user.id, "role": user.role}
    token = security.create_access_token(token_data)

    return {"access_token": token, "token_type": "bearer"}

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Employee:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("id") or -1)
        if user_id == -1:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.Employee).filter(models.Employee.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def get_current_admin(current_user: models.Employee = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

from app.schemas.auth import PasswordChangeRequest

@router.post("/auth/change-password")
def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    if not security.verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.password_hash = security.get_password_hash(request.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}
