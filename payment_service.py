from app.integrations.stripe import StripeClient
from app.schemas.payments import PaymentLinkCreate, PaymentLinkResponse


class PaymentService:
    def __init__(self, stripe_client: StripeClient):
        self.stripe_client = stripe_client

    async def create_payment_link(self, payload: PaymentLinkCreate) -> PaymentLinkResponse:
        result = await self.stripe_client.create_payment_link(
            product_name=payload.product_name,
            amount_cents=payload.amount_cents,
            currency=payload.currency,
            customer_email=payload.customer_email,
            metadata={
                "order_id": payload.order_id,
                "customer_email": payload.customer_email,
            },
        )
        return PaymentLinkResponse(
            payment_link_id=result["id"],
            url=result["url"],
        )

    async def handle_stripe_event(self, event: dict) -> dict:
        event_type = event.get("type")

        if event_type == "checkout.session.completed":
            return {
                "success": True,
                "received": True,
                "event_type": event_type,
                "action": "mark_order_as_paid",
            }

        return {
            "success": True,
            "received": True,
            "event_type": event_type,
            "action": "ignored",
        }