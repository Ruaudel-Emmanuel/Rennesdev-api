import uuid

from app.schemas.leads import LeadCreate, LeadResponse


class LeadService:
    async def create_lead(self, payload: LeadCreate) -> LeadResponse:
        lead_id = "lead_" + uuid.uuid4().hex[:12]
        return LeadResponse(
            lead_id=lead_id,
        )