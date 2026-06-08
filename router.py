# app/api/router.py
from fastapi import APIRouter

from app.api.v1 import (
    leads,
    quotes,
    contracts,
    payment_links,
    payments,
    invoices,
    orders,
)

api_router = APIRouter()

api_router.include_router(leads.router, prefix="/v1")
api_router.include_router(quotes.router, prefix="/v1")
api_router.include_router(contracts.router, prefix="/v1")
api_router.include_router(payment_links.router, prefix="/v1")
api_router.include_router(payments.router, prefix="/v1")
api_router.include_router(invoices.router, prefix="/v1")
api_router.include_router(orders.router, prefix="/v1")