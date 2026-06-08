# app/services/invoice_service.py
import uuid

from app.integrations.pdf_generator import PDFGenerator
from app.schemas.invoices import InvoiceCreate, InvoiceResponse


class InvoiceService:
    def __init__(self, pdf_generator: PDFGenerator):
        self.pdf_generator = pdf_generator

    async def create(self, payload: InvoiceCreate) -> InvoiceResponse:
        invoice_id = f"invoice_{uuid.uuid4().hex[:8]}"
        pdf_url = self.pdf_generator.create_fake_pdf(
            prefix=invoice_id,
            content=f"Facture pour {payload.customer_name} - {payload.service_name}",
        )
        return InvoiceResponse(invoice_id=invoice_id, pdf_url=pdf_url)