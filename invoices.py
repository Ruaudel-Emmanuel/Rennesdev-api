# app/schemas/invoices.py
from pydantic import BaseModel, EmailStr


class InvoiceCreate(BaseModel):
    order_id: str
    customer_name: str
    customer_email: EmailStr
    service_name: str
    amount_cents: int
    currency: str = "eur"


class InvoiceResponse(BaseModel):
    success: bool = True
    invoice_id: str
    pdf_url: str | None = None
    message: str = "Facture générée"