# app/services/lead_service.py
import uuid

from app.core.config import settings
from app.schemas.leads import LeadCreate, LeadResponse
from app.integrations.n8n import N8NClient


class LeadService:
    def __init__(self, n8n_client: N8NClient):
        self.n8n_client = n8n_client

    async def create(self, payload: LeadCreate) -> LeadResponse:
        lead_id = f"lead_{uuid.uuid4().hex[:8]}"
        data = payload.model_dump() | {"lead_id": lead_id}
        if settings.N8N_LEADS_WEBHOOK_URL:
            await self.n8n_client.send_lead(settings.N8N_LEADS_WEBHOOK_URL, data)
        return LeadResponse(lead_id=lead_id)