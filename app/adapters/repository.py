import abc
from datetime import datetime
from typing import List
from sqlmodel import Session, select

from app.models import (
    Currency,
    Wallet,
    Market,
    Transaction,
    WalletUpdate,
    User,
    Purchase,
    Settlement,
    SettlementUpdate,
)


class CurrencyRepository(abc.ABC):
    def create(self, *, session: Session, currency: Currency) -> Currency:
        db_obj = Currency.model_validate(currency)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


class WalletRepository(abc.ABC):
    def create(self, session: Session, wallet: Wallet) -> Wallet:
        db_obj = Wallet.model_validate(wallet)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update_instance(
        self, session: Session, wallet: Wallet, wallet_update: WalletUpdate
    ) -> Wallet:
        wallet_data = wallet_update.model_dump(exclude_unset=True)
        wallet.sqlmodel_update(wallet_data)
        session.add(wallet)
        return wallet

    def get_by_currency_for_update(
        self, session: Session, currency_id: int, user: User
    ) -> Wallet | None:
        statement = (
            select(Wallet)
            .where(Wallet.currency_id == currency_id)
            .where(Wallet.user_id == user.id)
            .with_for_update()
        )
        wallet = session.exec(statement).first()
        if not wallet:
            return None
        return wallet


class TransactionRepository(abc.ABC):
    def new(self, session: Session, transaction: Transaction) -> Transaction:
        db_obj = Transaction.model_validate(transaction)
        session.add(db_obj)
        return db_obj

    def get_by_currency_for_update(
        self, session: Session, currency_id: int
    ) -> Wallet | None:
        statement = (
            select(Wallet).where(Wallet.currency_id == currency_id).with_for_update()
        )
        wallet = session.exec(statement).first()
        if not wallet:
            return None
        return wallet


class MarketRepository(abc.ABC):
    def create(self, session: Session, market: Market) -> Market:
        db_obj = Market.model_validate(market)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_by_id(self, session: Session, id: int) -> Market:
        statement = select(Market).where(Market.id == id)
        settlement = session.exec(statement).first()
        return settlement


class PurchaseRepository(abc.ABC):

    def get_by_id(self, session: Session, id: str) -> Purchase:
        purchase = select(Purchase).where(Purchase.id == id)
        settlement = session.exec(purchase).first()
        return settlement

    def new(self, session: Session, purchase: Purchase) -> Purchase:
        db_obj = Purchase.model_validate(purchase)
        session.add(db_obj)
        return db_obj


class SettlementRepository(abc.ABC):
    def create(self, session: Session, settlement: Settlement) -> Settlement:
        db_obj = Settlement.model_validate(settlement)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_active_lock(self, session: Session, market_id: int) -> Settlement:
        statement = (
            select(Settlement)
            .where(Settlement.market_id == market_id)
            .where(Settlement.active == True)
            .with_for_update()
        )
        settlement = session.exec(statement).first()
        return settlement

    def update_instance(
        self, session: Session,
        settlemet: Settlement,
        settlement_update: SettlementUpdate,
    ) -> Settlement:
        settlement_data = settlement_update.model_dump(exclude_unset=True)
        settlemet.sqlmodel_update(settlement_data)
        session.add(settlemet)
        return settlemet
