# app/services/quote_service.py
import uuid

from app.core.config import settings
from app.integrations.n8n import N8NClient
from app.integrations.pdf_generator import PDFGenerator
from app.schemas.quotes import QuoteCreate, QuoteResponse


class QuoteService:
    def __init__(self, n8n_client: N8NClient, pdf_generator: PDFGenerator):
        self.n8n_client = n8n_client
        self.pdf_generator = pdf_generator

    async def create(self, payload: QuoteCreate) -> QuoteResponse:
        quote_id = f"quote_{uuid.uuid4().hex[:8]}"
        pdf_url = self.pdf_generator.create_fake_pdf(
            prefix=quote_id,
            content=f"Devis pour {payload.customer_name} - {payload.service_name}",
        )
        data = payload.model_dump() | {"quote_id": quote_id, "pdf_url": pdf_url}
        if settings.N8N_QUOTES_WEBHOOK_URL:
            await self.n8n_client.send_quote(settings.N8N_QUOTES_WEBHOOK_URL, data)
        return QuoteResponse(quote_id=quote_id, pdf_url=pdf_url)