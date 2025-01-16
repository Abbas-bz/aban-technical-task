import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser, get_purchase_service
from app.core.config import settings
from app.models import Purchase, Market, PurchaseRequest
from app.service import PurchaseService

router = APIRouter()


@router.post("/", dependencies=[Depends(get_current_active_superuser)])
def create_purchase(
    *,
    session: SessionDep,
    purchase_request: PurchaseRequest,
    purchase_service: PurchaseService = Depends(get_purchase_service),
) -> Any:
    """
    Make a new purchase.
    """
    market = session.exec(
        select(Market).where(Market.symbol == purchase_request.market)
    ).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market ID not found")
    purchase = purchase_service.purchase(market, purchase_request.amount)
    return purchase
