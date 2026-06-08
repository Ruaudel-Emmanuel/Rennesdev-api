# app/schemas/payments.py
from pydantic import BaseModel


class PaymentLinkCreate(BaseModel):
    order_id: str
    product_name: str
    amount_cents: int
    currency: str = "eur"
    customer_email: str | None = None


class PaymentLinkResponse(BaseModel):
    success: bool = True
    payment_link_id: str
    url: str
    message: str = "Lien de paiement créé"