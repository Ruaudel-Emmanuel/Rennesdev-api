# app/schemas/quotes.py
from pydantic import BaseModel, EmailStr


class QuoteCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    company: str | None = None
    service_name: str
    amount_cents: int
    currency: str = "eur"
    description: str | None = None


class QuoteResponse(BaseModel):
    success: bool = True
    quote_id: str
    pdf_url: str | None = None
    message: str = "Devis généré"