# app/schemas/leads.py
from pydantic import BaseModel, EmailStr


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    company: str | None = None
    need: str
    budget: str | None = None
    source: str = "website"


class LeadResponse(BaseModel):
    success: bool = True
    lead_id: str
    message: str = "Lead enregistré"