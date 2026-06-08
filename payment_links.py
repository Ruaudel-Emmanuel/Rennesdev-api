# app/api/v1/quotes.py
from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_quote_service
from app.core.security import verify_api_key
from app.schemas.quotes import QuoteCreate, QuoteResponse
from app.services.quote_service import QuoteService

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post(
    "",
    response_model=QuoteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
async def create_quote(
    payload: QuoteCreate,
    service: QuoteService = Depends(get_quote_service),
):
    return await service.create(payload)