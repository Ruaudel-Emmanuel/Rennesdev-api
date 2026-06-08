import uuid

from app.schemas.invoices import InvoiceCreate, InvoiceResponse


class InvoiceService:
    async def create_invoice(self, payload: InvoiceCreate) -> InvoiceResponse:
        invoice_id = "invoice_" + uuid.uuid4().hex[:12]
        return InvoiceResponse(
            invoice_id=invoice_id,
            pdf_url="storage/%s.pdf" % invoice_id,
        )