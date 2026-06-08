from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.api.dependencies import get_payment_service
from app.core.config import settings
from app.integrations.stripe import StripeClient
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/webhook/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(default=None, alias="stripe-signature"),
    service: PaymentService = Depends(get_payment_service),
):
    payload = await request.body()

    client = StripeClient(
        secret_key=settings.STRIPE_SECRET_KEY,
        webhook_secret=settings.STRIPE_WEBHOOK_SECRET,
    )

    try:
        event = client.verify_webhook_signature(payload, stripe_signature)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook: %s" % exc)

    return await service.handle_stripe_event(event)