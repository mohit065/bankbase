from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"
    reversal = "reversal"

class TransactionBase(BaseModel):
    sender_id: Optional[int] = None
    recv_id: Optional[int] = None
    amount: float
    type: TransactionType

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    timestamp: datetime
    reversed: bool = False
    model_config = ConfigDict(from_attributes=True)

class ReversalResult(BaseModel):
    original: Transaction
    reversal: Transaction
