from logging import getLogger
from decimal import Decimal

from sqlalchemy.exc import OperationalError
from app.adapters import PurchaseRepository, SettlementRepository, MarketRepository
from app.models import Settlement, SettlementUpdate
from .celery import app
from app.core.db import engine
from sqlmodel import Session

logger = getLogger(__name__)

THRESHOLD = 10.0


@app.task(bind=True)
def settle_purchase(self, *, purchase: str) -> None:
    try:
        with Session(engine).no_autoflush as session:
            purchase = PurchaseRepository().get_by_id(session, purchase)
            market = MarketRepository().get_by_id(session, purchase.market_id)
            settlement_repository = SettlementRepository()
            settlement = SettlementRepository().get_active_lock(
                session, purchase.market_id
            )
            if not settlement:
                settlement = Settlement(amount=Decimal(0.0), active=True, market_id=market.id)
                settlement = settlement_repository.create(session, settlement)

            settlement_update = SettlementUpdate(
                amount=purchase.amount + settlement.amount
            )
            settlement = settlement_repository.update_instance(
                session, settlement, settlement_update
            )
            # If threshold is reached, process the batch
            if (settlement.amount * market.price) >= THRESHOLD:
                settlement_update = SettlementUpdate(active=False)
                settlement = settlement_repository.update_instance(
                    session, settlement, settlement_update
                )
                buy_from_exchange(market.symbol, settlement.amount) 
            session.commit()
    except OperationalError:
        # TODO: Handle dead lock or etc
        pass


def buy_from_exchange(market_symbol: str, amount: Decimal):
    # Simulated third-party API request
    print(f"Sending data to third party: {market_symbol} {amount}")
