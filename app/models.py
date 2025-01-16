import uuid
import enum
from datetime import datetime, timezone
from typing import Optional

from decimal import Decimal
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Column, Enum


class BaseTable(SQLModel):
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )


class Currency(BaseTable, table=True):
    __tablename__ = "currencies"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    symbol: str


class Market(BaseTable, table=True):
    __tablename__ = "markets"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    symbol: str
    active: bool
    price: Decimal = Field(default=0, max_digits=16, decimal_places=6)
    base_currency_id: int = Field(
        foreign_key="currencies.id", nullable=False, ondelete="CASCADE"
    )
    qoute_currency_id: int = Field(
        foreign_key="currencies.id", nullable=False, ondelete="CASCADE"
    )


class WalletUpdate(SQLModel):
    name: str | None = None
    balance: Decimal | None = None
    locked: Decimal | None = None
    reserved: Decimal | None = None
    active: bool | None = None
    currency_id: int | None = None
    user_id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Wallet(BaseTable, table=True):
    __tablename__ = "wallets"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    balance: Decimal = Field(default=0, max_digits=16, decimal_places=6)
    locked: Decimal = Field(default=0, max_digits=16, decimal_places=6)
    reserved: Decimal = Field(default=0, max_digits=16, decimal_places=6)
    active: bool
    currency_id: int = Field(
        foreign_key="currencies.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, ondelete="CASCADE"
    )


class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    FAILED = "FAILED"
    DONE = "DONE"


class TransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBT = "DEBT"


class Transaction(BaseTable, table=True):
    __tablename__ = "transactions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    amount: Decimal = Field(default=0, max_digits=16, decimal_places=6)
    status: TransactionStatus = Field(sa_column=Column(Enum(TransactionStatus)))
    type: TransactionType = Field(sa_column=Column(Enum(TransactionType)))
    wallet_id: uuid.UUID = Field(
        foreign_key="wallets.id", nullable=False, ondelete="CASCADE"
    )


class PurchaseStatus(str, enum.Enum):
    PENDING = "PENDING"
    FAILED = "FAILED"
    DONE = "DONE"


class PurchaseRequest(SQLModel):
    amount: Decimal
    market: str


class Purchase(BaseTable, table=True):
    __tablename__ = "purchases"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: PurchaseStatus = Field(sa_column=Column(Enum(PurchaseStatus)))
    amount: Decimal = Field(default=0, max_digits=16, decimal_places=6)
    price: Decimal = Field(default=0, max_digits=16, decimal_places=6)
    user_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, ondelete="CASCADE"
    )
    market_id: int = Field(foreign_key="markets.id", nullable=False, ondelete="CASCADE")


class Settlement(BaseTable, table=True):
    __tablename__ = "settlements"
    id: int | None = Field(default=None, primary_key=True)
    transaction_code: str | None = Field(nullable=True)
    active: bool
    amount: Decimal = Field(default=0, max_digits=16, decimal_places=6)
    market_id: int = Field(foreign_key="markets.id", nullable=False, ondelete="CASCADE")


class SettlementUpdate(BaseTable):
    transaction_code: str | None = None
    active: bool | None = None
    market_id: int | None = None
    amount: Decimal | None = None


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr | None = Field(default=None, max_length=255)
    full_name: str
    verified: bool = Field(default=False)
    hashed_password: str
    is_superuser: bool = Field(default=False)


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
