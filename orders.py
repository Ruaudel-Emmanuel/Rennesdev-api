# app/schemas/orders.py
from pydantic import BaseModel, EmailStr


class ConsultingOrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    company: str | None = None
    offer_code: str
    amount_cents: int
    currency: str = "eur"
    needs_contract: bool = True


class OrderResponse(BaseModel):
    success: bool = True
    order_id: str
    quote_id: str | None = None
    contract_id: str | None = None
    payment_link_url: str | None = None
    invoice_id: str | None = None
    status: str