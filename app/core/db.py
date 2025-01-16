from sqlmodel import Session, create_engine, select

from app.adapters import WalletRepository, CurrencyRepository, MarketRepository
from app.core.config import settings
from app.models import User, UserCreate, Wallet, Market, Currency
from app import crud
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name=settings.FIRST_SUPERUSER,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

    base_currency = session.exec(
        select(Currency).where(Currency.symbol == settings.BASE_CURRENCY_SYMBOL)
    ).first()
    if not base_currency:
        base_currency_in = Currency(
            symbol=settings.BASE_CURRENCY_SYMBOL,
            name=settings.BASE_CURRENCY_SYMBOL,
        )
        base_currency = CurrencyRepository().create(session=session, currency=base_currency_in)


    qoute_currency = session.exec(
        select(Currency).where(Currency.symbol == settings.QOUTE_CURRENCY_SYMBOL)
    ).first()
    if not qoute_currency:
        qoute_currency_in = Currency(
            symbol=settings.QOUTE_CURRENCY_SYMBOL,
            name=settings.QOUTE_CURRENCY_SYMBOL,
        )
        qoute_currency = CurrencyRepository().create(session=session, currency=qoute_currency_in)

    base_wallet = session.exec(
        select(Wallet).where(Wallet.user_id == user.id).where(Wallet.currency_id == base_currency.id)
    ).first()
    if not base_wallet:
        base_wallet_in = Wallet(
            name=base_currency.symbol,
            balance=20,
            active=True,
            currency_id=base_currency.id,
            user_id=user.id
        )
        base_wallet = WalletRepository().create(session=session, wallet=base_wallet_in)


    qoute_wallet = session.exec(
        select(Wallet).where(Wallet.user_id == user.id).where(Wallet.currency_id == qoute_currency.id)
    ).first()
    if not qoute_wallet:
        qoute_wallet_in = Wallet(
            name=qoute_currency.symbol,
            balance=20,
            active=True,
            currency_id=qoute_currency.id,
            user_id=user.id
        )
        qoute_wallet = WalletRepository().create(session=session, wallet=qoute_wallet_in)

    market = session.exec(
        select(Market).where(Market.base_currency_id == base_currency.id)
    ).first()
    if not market:
        market_in = Market(
            name=settings.BASE_CURRENCY_SYMBOL + settings.QOUTE_CURRENCY_SYMBOL,
            base_currency_id=base_currency.id,
            qoute_currency_id=qoute_currency.id,
            symbol=settings.BASE_CURRENCY_SYMBOL + settings.QOUTE_CURRENCY_SYMBOL,
            active=True,
            price=4
        )
        market = MarketRepository().create(session=session, market=market_in)
