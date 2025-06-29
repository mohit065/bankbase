from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.database import get_db
from app.schemas import account as account_schema
from app.api.auth import get_current_user, get_current_admin

router = APIRouter()

@router.post("/accounts", response_model=account_schema.Account)
def create_account(
    account_data: account_schema.AccountCreate,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_admin)
):
    if db.query(models.Account).filter(models.Account.email == account_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    if db.query(models.Account).filter(models.Account.PID == account_data.PID).first():
        raise HTTPException(status_code=400, detail="PID already exists")

    account = models.Account(**account_data.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@router.put("/accounts/{account_id}", response_model=account_schema.Account)
def update_account(
    account_id: int,
    updates: account_schema.AccountUpdate,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)
    return account

@router.get("/accounts", response_model=List[account_schema.Account])
def get_all_accounts(
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    return db.query(models.Account).all()

@router.get("/accounts/{account_id}", response_model=account_schema.Account)
def get_account_by_id(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.patch("/accounts/{account_id}/toggle-active", response_model=account_schema.Account)
def toggle_account_active_status(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_admin)
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.is_active = not account.is_active
    db.commit()
    db.refresh(account)
    return account

@router.delete("/accounts/{account_id}", status_code=204)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_admin)
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    db.commit()
    return
