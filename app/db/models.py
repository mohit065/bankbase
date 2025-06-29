import enum
from datetime import datetime, UTC
from sqlalchemy import ForeignKey
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    joined_on: Mapped[datetime] = mapped_column(default=datetime.now(UTC))


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    PID: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(nullable=True)
    balance: Mapped[float] = mapped_column(default=0.0)
    created_on: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    is_active: Mapped[bool] = mapped_column(default=True)

    sent_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", foreign_keys="[Transaction.sender_id]",
        back_populates="sender", cascade="all, delete"
    )

    received_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", foreign_keys="[Transaction.recv_id]",
        back_populates="receiver", cascade="all, delete"
    )


class TransactionType(enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"
    reversal = "reversal"

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sender_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    recv_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    amount: Mapped[float] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    reversed: Mapped[bool] = mapped_column(default=False)
    type: Mapped[TransactionType] = mapped_column(SqlEnum(TransactionType), default=TransactionType.transfer, nullable=False)

    sender: Mapped["Account"] = relationship("Account", foreign_keys=[sender_id], back_populates="sent_transactions")
    receiver: Mapped["Account"] = relationship("Account", foreign_keys=[recv_id], back_populates="received_transactions")