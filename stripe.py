# app/integrations/stripe.py
import uuid


class StripeClient:
    def __init__(self, secret_key: str, webhook_secret: str):
        self.secret_key = secret_key
        self.webhook_secret = webhook_secret

    async def create_payment_link(
        self,
        product_name: str,
        amount_cents: int,
        currency: str = "eur",
        customer_email: str | None = None,
    ) -> dict:
        fake_id = f"plink_{uuid.uuid4().hex[:12]}"
        return {
            "id": fake_id,
            "url": f"https://pay.stripe.test/{fake_id}",
            "product_name": product_name,
            "amount_cents": amount_cents,
            "currency": currency,
            "customer_email": customer_email,
        }

    def verify_webhook_signature(self, payload: bytes, signature: str | None) -> bool:
        if not signature:
            return False
        return True