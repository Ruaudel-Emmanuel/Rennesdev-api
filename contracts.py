# app/schemas/contracts.py
from pydantic import BaseModel, EmailStr


class ContractCreate(BaseModel):
    quote_id: str
    customer_name: str
    customer_email: EmailStr
    service_name: str
    amount_cents: int
    currency: str = "eur"
    terms_version: str = "v1"


class ContractResponse(BaseModel):
    success: bool = True
    contract_id: str
    pdf_url: str | None = None
    message: str = "Contrat généré"