import uuid

from app.schemas.quotes import QuoteCreate, QuoteResponse


class QuoteService:
    async def create_quote(self, payload: QuoteCreate) -> QuoteResponse:
        quote_id = "quote_" + uuid.uuid4().hex[:12]
        return QuoteResponse(
            quote_id=quote_id,
            pdf_url="storage/%s.pdf" % quote_id,
        )