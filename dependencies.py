from app.core.config import settings
from app.integrations.stripe import StripeClient
from app.services.contract_service import ContractService
from app.services.invoice_service import InvoiceService
from app.services.lead_service import LeadService
from app.services.payment_service import PaymentService
from app.services.quote_service import QuoteService


def get_lead_service() -> LeadService:
    return LeadService()


def get_quote_service() -> QuoteService:
    return QuoteService()


def get_contract_service() -> ContractService:
    return ContractService()


def get_invoice_service() -> InvoiceService:
    return InvoiceService()


def get_payment_service() -> PaymentService:
    stripe_client = StripeClient(
        secret_key=settings.STRIPE_SECRET_KEY,
        webhook_secret=settings.STRIPE_WEBHOOK_SECRET,
    )
    return PaymentService(stripe_client=stripe_client)