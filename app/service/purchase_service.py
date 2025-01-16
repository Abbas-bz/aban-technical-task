import logging
from sqlmodel import Session
from app.models import Market, User, Transaction, Wallet, WalletUpdate, Purchase
from decimal import Decimal
from app.adapters import WalletRepository, TransactionRepository, PurchaseRepository
from fastapi import HTTPException
from app.worker.tasks import settle_purchase

logger = logging.getLogger(__name__)


class PurchaseService:
    """
    scrolls through pages in the given channel and fetches data.
    """

    def __init__(self, db_session: Session, user: User) -> None:
        self.db_session = db_session
        self.user = user

    def purchase(self, market: Market, amount: Decimal) -> Purchase:
        qoute_wallet = self.get_user_wallet(market.qoute_currency_id)
        base_wallet = self.get_user_wallet(market.base_currency_id)
        self.check_user_balance(qoute_wallet, amount * market.price)
        self.make_transaction(base_wallet, qoute_wallet, amount, market.price)
        purchase = self.create_purchase(market, amount, amount * market.price)
        self.db_session.commit()
        self.db_session.refresh(purchase)
        self.settle_with_exchange(purchase)

        return purchase

    def get_user_wallet(self, currency_id: int) -> Wallet:
        wallet = WalletRepository().get_by_currency_for_update(
            self.db_session, currency_id, self.user
        )
        if not wallet:
            raise HTTPException(status_code=404, detail="No wallet found")
        return wallet

    def check_user_balance(self, wallet: Wallet, total_price: Decimal) -> bool:
        if (wallet.balance - wallet.locked) >= total_price:
            return True
        raise HTTPException(status_code=422, detail="Not enough credit")

    def make_transaction(
        self, base_wallet: Wallet, qoute_wallet: Wallet, amount: Decimal, price: Decimal
    ) -> bool:
        base_wallet_update = WalletUpdate(balance=base_wallet.balance + amount)

        qoute_wallet_update = WalletUpdate(
            balance=qoute_wallet.balance - (amount * price)
        )
        wallet_repository = WalletRepository()
        wallet_repository.update_instance(
            self.db_session, base_wallet, base_wallet_update
        )
        wallet_repository.update_instance(
            self.db_session, qoute_wallet, qoute_wallet_update
        )

        base_transaction = Transaction(
            amount=amount,
            status="DONE",
            type="CREDIT",
            wallet_id=base_wallet.id,
        )

        qoute_transaction = Transaction(
            amount=amount * price,
            status="DONE",
            type="CREDIT",
            wallet_id=qoute_wallet.id,
        )

        transaction_repository = TransactionRepository()
        transaction_repository.new(self.db_session, base_transaction)
        transaction_repository.new(self.db_session, qoute_transaction)

    def create_purchase(self, market: Market, amount: Decimal, price: Decimal):
        purchase = Purchase(
            status="DONE",
            amount=amount,
            price=price,
            user_id=self.user.id,
            market_id=market.id,
        )

        return PurchaseRepository().new(self.db_session, purchase)

    def settle_with_exchange(self, purchase: Purchase):
        settle_purchase.delay(purchase=purchase.id)
