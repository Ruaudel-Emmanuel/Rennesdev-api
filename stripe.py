from typing import Any, Dict, Optional

import stripe


class StripeClient:
    def __init__(self, secret_key: str, webhook_secret: str):
        self.secret_key = secret_key
        self.webhook_secret = webhook_secret
        stripe.api_key = self.secret_key

    async def create_payment_link(
        self,
        product_name: str,
        amount_cents: int,
        currency: str = "eur",
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        payment_link = stripe.PaymentLink.create(
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": amount_cents,
                        "product_data": {
                            "name": product_name,
                        },
                    },
                    "quantity": 1,
                }
            ],
            metadata=metadata or {},
            after_completion={
                "type": "redirect",
                "redirect": {
                    "url": "https://rennesdev.fr/merci"
                },
            },
            allow_promotion_codes=False,
        )

        return {
            "id": payment_link["id"],
            "url": payment_link["url"],
            "raw": payment_link,
            "customer_email": customer_email,
        }

    def verify_webhook_signature(self, payload: bytes, signature: Optional[str]) -> Dict[str, Any]:
        if not signature:
            raise ValueError("Missing Stripe-Signature header")

        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=self.webhook_secret,
        )
        return event