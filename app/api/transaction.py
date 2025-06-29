from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db import models
from app.db.database import get_db
from app.schemas import transaction as transaction_schema
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/transactions", response_model=transaction_schema.Transaction)
def create_transaction(
    tx: transaction_schema.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    if tx.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    if tx.type == transaction_schema.TransactionType.deposit:
        if tx.sender_id is not None or tx.recv_id is None:
            raise HTTPException(status_code=400, detail="Deposit must have recv_id only")
    elif tx.type == transaction_schema.TransactionType.withdrawal:
        if tx.sender_id is None or tx.recv_id is not None:
            raise HTTPException(status_code=400, detail="Withdrawal must have sender_id only")
    elif tx.type == transaction_schema.TransactionType.transfer:
        if not tx.sender_id or not tx.recv_id:
            raise HTTPException(status_code=400, detail="Transfer must have both sender_id and recv_id")
    elif tx.type == transaction_schema.TransactionType.reversal:
        raise HTTPException(status_code=400, detail="You cannot create a reversal directly")

    if tx.sender_id:
        sender = db.query(models.Account).filter(models.Account.id == tx.sender_id).first()
        if not sender:
            raise HTTPException(status_code=404, detail="Sender account not found")
    if tx.recv_id:
        receiver = db.query(models.Account).filter(models.Account.id == tx.recv_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver account not found")

    transaction = models.Transaction(**tx.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/transactions", response_model=List[transaction_schema.Transaction])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    return db.query(models.Transaction).all()


@router.post("/transactions/{transaction_id}/reverse", response_model=transaction_schema.ReversalResult)
def reverse_transaction(
    transaction_id: int = Path(..., description="ID of the transaction to reverse"),
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can reverse transactions")

    original_tx = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not original_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if original_tx.reversed:
        raise HTTPException(status_code=400, detail="Transaction is already reversed")

    if original_tx.type == transaction_schema.TransactionType.reversal:
        raise HTTPException(status_code=400, detail="Cannot reverse a reversal transaction")

    original_tx.reversed = True

    reversal_tx = models.Transaction(
        sender_id=original_tx.recv_id,
        recv_id=original_tx.sender_id,
        amount=original_tx.amount,
        type=transaction_schema.TransactionType.reversal
    )

    db.add(reversal_tx)
    db.commit()
    db.refresh(original_tx)
    db.refresh(reversal_tx)

    return {
        "original": original_tx,
        "reversal": reversal_tx
    }


@router.get("/transactions/by-date", response_model=List[transaction_schema.Transaction])
def filter_transactions_by_date(
    start: datetime = Query(..., description="Start date (inclusive)"),
    end: datetime = Query(..., description="End date (inclusive)"),
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    query = db.query(models.Transaction).filter(
        models.Transaction.timestamp >= start,
        models.Transaction.timestamp <= end
    )

    if current_user.role != "admin":
        query = query.join(models.Account, models.Transaction.sender_id == models.Account.id)

    return query.all()


@router.get("/transactions/by-account/{account_id}", response_model=List[transaction_schema.Transaction])
def filter_transactions_by_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = db.query(models.Transaction).filter(
        (models.Transaction.sender_id == account_id) |
        (models.Transaction.recv_id == account_id)
    ).all()

    return transactions
