from pathlib import Path
from datetime import datetime
import shutil
import sys
import importlib


ROOT = Path(__file__).resolve().parent
BACKUP_DIR = ROOT / "_backup_before_repair" / datetime.now().strftime("%Y%m%d_%H%M%S")


FILES = {
    "app/main.py": """from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Application starting")
    yield
    logger.info("Application stopping")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")
""",

    "app/api/router.py": """from fastapi import APIRouter

from app.api.v1 import contracts, invoices, leads, orders, payments, quotes

api_router = APIRouter()
api_router.include_router(leads.router)
api_router.include_router(quotes.router)
api_router.include_router(contracts.router)
api_router.include_router(invoices.router)
api_router.include_router(payments.router)
api_router.include_router(orders.router)
""",

    "app/api/dependencies.py": """from app.core.config import settings
from app.integrations.stripe import StripeClient
from app.services.contract_service import ContractService
from app.services.invoice_service import InvoiceService
from app.services.lead_service import LeadService
from app.services.order_service import OrderService
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


def get_order_service() -> OrderService:
    return OrderService()


def get_payment_service() -> PaymentService:
    stripe_client = StripeClient(
        secret_key=settings.STRIPE_SECRET_KEY,
        webhook_secret=settings.STRIPE_WEBHOOK_SECRET,
    )
    return PaymentService(stripe_client=stripe_client)
""",

    "app/api/v1/leads.py": """from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import get_lead_service
from app.core.config import settings
from app.schemas.leads import LeadCreate, LeadResponse
from app.services.lead_service import LeadService

router = APIRouter(tags=["leads"])


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    x_api_key: str = Header(...),
    service: LeadService = Depends(get_lead_service),
):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return await service.create_lead(payload)
""",

    "app/api/v1/quotes.py": """from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import get_quote_service
from app.core.config import settings
from app.schemas.quotes import QuoteCreate, QuoteResponse
from app.services.quote_service import QuoteService

router = APIRouter(tags=["quotes"])


@router.post("/quotes", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    payload: QuoteCreate,
    x_api_key: str = Header(...),
    service: QuoteService = Depends(get_quote_service),
):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return await service.create_quote(payload)
""",

    "app/api/v1/contracts.py": """from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import get_contract_service
from app.core.config import settings
from app.schemas.contracts import ContractCreate, ContractResponse
from app.services.contract_service import ContractService

router = APIRouter(tags=["contracts"])


@router.post("/contracts", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    payload: ContractCreate,
    x_api_key: str = Header(...),
    service: ContractService = Depends(get_contract_service),
):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return await service.create_contract(payload)
""",

    "app/api/v1/invoices.py": """from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import get_invoice_service
from app.core.config import settings
from app.schemas.invoices import InvoiceCreate, InvoiceResponse
from app.services.invoice_service import InvoiceService

router = APIRouter(tags=["invoices"])


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    x_api_key: str = Header(...),
    service: InvoiceService = Depends(get_invoice_service),
):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return await service.create_invoice(payload)
""",

    "app/api/v1/orders.py": """from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import get_order_service
from app.core.config import settings
from app.schemas.orders import ConsultingOrderCreate, ConsultingOrderResponse
from app.services.order_service import OrderService

router = APIRouter(tags=["orders"])


@router.post(
    "/orders/consulting-session",
    response_model=ConsultingOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_consulting_order(
    payload: ConsultingOrderCreate,
    x_api_key: str = Header(...),
    service: OrderService = Depends(get_order_service),
):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return await service.create_consulting_order(payload)
""",

    "app/api/v1/payments.py": """from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.api.dependencies import get_payment_service
from app.schemas.payments import PaymentLinkCreate, PaymentLinkResponse
from app.services.payment_service import PaymentService

router = APIRouter(tags=["payments"])


@router.post("/payment-links", response_model=PaymentLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_link(
    payload: PaymentLinkCreate,
    x_api_key: str = Header(...),
    service: PaymentService = Depends(get_payment_service),
):
    from app.core.config import settings

    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return await service.create_payment_link(payload)


@router.post("/payments/webhook/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    service: PaymentService = Depends(get_payment_service),
):
    payload = await request.body()

    try:
        event = service.stripe_client.verify_webhook_signature(payload, stripe_signature)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return await service.handle_stripe_event(event)
""",

    "app/core/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "api-rennesdev"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "dev"

    API_KEY: str = "change-me"

    N8N_LEADS_WEBHOOK_URL: str = ""
    N8N_QUOTES_WEBHOOK_URL: str = ""
    N8N_ORDERS_WEBHOOK_URL: str = ""

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
""",

    "app/core/logging.py": """import logging
import logging.config
from pathlib import Path
from typing import Union


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = LOG_DIR / "app.log"


def build_logging_config(
    log_level: str = DEFAULT_LOG_LEVEL,
    log_file: Union[str, Path] = DEFAULT_LOG_FILE,
) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
    }


def setup_logging(log_level: str = DEFAULT_LOG_LEVEL) -> None:
    logging.config.dictConfig(build_logging_config(log_level=log_level))


def get_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(name)
""",

    "app/integrations/stripe.py": """from typing import Any, Dict, Optional

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
        if not self.secret_key:
            return {
                "id": "plink_dev_123",
                "url": "https://example.com/pay/dev-link",
                "raw": {},
                "customer_email": customer_email,
            }

        payment_link = stripe.PaymentLink.create(
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": amount_cents,
                        "product_data": {"name": product_name},
                    },
                    "quantity": 1,
                }
            ],
            metadata=metadata or {},
        )

        return {
            "id": payment_link["id"],
            "url": payment_link["url"],
            "raw": payment_link,
            "customer_email": customer_email,
        }

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: Optional[str],
    ) -> Dict[str, Any]:
        if not signature:
            raise ValueError("Missing Stripe-Signature header")

        if not self.webhook_secret:
            return {"type": "checkout.session.completed"}

        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=self.webhook_secret,
        )
        return event
""",

    "app/schemas/leads.py": """from typing import Optional

from pydantic import BaseModel, EmailStr


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    need: str
    budget: Optional[str] = None
    source: str = "website"


class LeadResponse(BaseModel):
    success: bool = True
    lead_id: str
    message: str = "Lead enregistré"
""",

    "app/schemas/quotes.py": """from typing import Optional

from pydantic import BaseModel, EmailStr


class QuoteCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    company: str
    service_name: str
    amount_cents: int
    currency: str = "eur"
    description: Optional[str] = None


class QuoteResponse(BaseModel):
    success: bool = True
    quote_id: str
    pdf_url: Optional[str] = None
    message: str = "Devis généré"
""",

    "app/schemas/contracts.py": """from typing import Optional

from pydantic import BaseModel, EmailStr


class ContractCreate(BaseModel):
    quote_id: str
    customer_name: str
    customer_email: EmailStr
    service_name: str
    amount_cents: int
    currency: str = "eur"
    terms_version: str = "v1"


class ContractResponse(BaseModel):
    success: bool = True
    contract_id: str
    pdf_url: Optional[str] = None
    message: str = "Contrat généré"
""",

    "app/schemas/invoices.py": """from typing import Optional

from pydantic import BaseModel, EmailStr


class InvoiceCreate(BaseModel):
    order_id: str
    customer_name: str
    customer_email: EmailStr
    service_name: str
    amount_cents: int
    currency: str = "eur"


class InvoiceResponse(BaseModel):
    success: bool = True
    invoice_id: str
    pdf_url: Optional[str] = None
    message: str = "Facture générée"
""",

    "app/schemas/orders.py": """from typing import Optional

from pydantic import BaseModel, EmailStr


class ConsultingOrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    company: str
    offer_code: str
    amount_cents: int
    currency: str = "eur"
    needs_contract: bool = True


class ConsultingOrderResponse(BaseModel):
    success: bool = True
    status: str
    order_id: str
    quote_id: str
    contract_id: Optional[str] = None
    payment_link_url: Optional[str] = None
""",

    "app/schemas/payments.py": """from pydantic import BaseModel, EmailStr


class PaymentLinkCreate(BaseModel):
    order_id: str
    product_name: str
    amount_cents: int
    currency: str = "eur"
    customer_email: EmailStr


class PaymentLinkResponse(BaseModel):
    success: bool = True
    payment_link_id: str
    url: str
    message: str = "Lien de paiement créé"
""",

    "app/services/lead_service.py": """import uuid

from app.schemas.leads import LeadCreate, LeadResponse


class LeadService:
    async def create_lead(self, payload: LeadCreate) -> LeadResponse:
        lead_id = "lead_" + uuid.uuid4().hex[:12]
        return LeadResponse(
            lead_id=lead_id,
            message="Lead enregistré",
        )
""",

    "app/services/quote_service.py": """import uuid

from app.schemas.quotes import QuoteCreate, QuoteResponse


class QuoteService:
    async def create_quote(self, payload: QuoteCreate) -> QuoteResponse:
        quote_id = "quote_" + uuid.uuid4().hex[:12]
        return QuoteResponse(
            quote_id=quote_id,
            pdf_url=f"/storage/{quote_id}.pdf",
            message="Devis généré",
        )
""",

    "app/services/contract_service.py": """import uuid

from app.schemas.contracts import ContractCreate, ContractResponse


class ContractService:
    async def create_contract(self, payload: ContractCreate) -> ContractResponse:
        contract_id = "contract_" + uuid.uuid4().hex[:12]
        return ContractResponse(
            contract_id=contract_id,
            pdf_url=f"/storage/{contract_id}.pdf",
            message="Contrat généré",
        )
""",

    "app/services/invoice_service.py": """import uuid

from app.schemas.invoices import InvoiceCreate, InvoiceResponse


class InvoiceService:
    async def create_invoice(self, payload: InvoiceCreate) -> InvoiceResponse:
        invoice_id = "invoice_" + uuid.uuid4().hex[:12]
        return InvoiceResponse(
            invoice_id=invoice_id,
            pdf_url=f"/storage/{invoice_id}.pdf",
            message="Facture générée",
        )
""",

    "app/services/order_service.py": """import uuid

from app.schemas.orders import ConsultingOrderCreate, ConsultingOrderResponse


class OrderService:
    async def create_consulting_order(
        self,
        payload: ConsultingOrderCreate,
    ) -> ConsultingOrderResponse:
        order_id = "order_" + uuid.uuid4().hex[:12]
        quote_id = "quote_" + uuid.uuid4().hex[:12]
        contract_id = "contract_" + uuid.uuid4().hex[:12] if payload.needs_contract else None

        return ConsultingOrderResponse(
            success=True,
            status="pending_payment",
            order_id=order_id,
            quote_id=quote_id,
            contract_id=contract_id,
            payment_link_url="https://example.com/pay/dev-link",
        )
""",

    "app/services/payment_service.py": """from app.integrations.stripe import StripeClient
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
        return {
            "success": True,
            "received": True,
            "event_type": event_type,
        }
""",

    "tests/conftest.py": """import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def api_headers():
    return {
        "x-api-key": settings.API_KEY,
    }
""",

    "tests/api/test_root.py": """def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
""",

    "tests/api/test_health.py": """def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
""",

    "tests/api/test_leads.py": """def test_create_lead_requires_api_key(client):
    payload = {
        "name": "Jean Dupont",
        "email": "jean@example.com",
        "company": "BTP Dupont",
        "need": "Automatiser mes devis",
        "budget": "2000-5000",
        "source": "website"
    }

    response = client.post("/api/v1/leads", json=payload)
    assert response.status_code in (401, 422)
""",

    "tests/api/test_payments_webhook.py": """def test_stripe_webhook_missing_signature(client):
    response = client.post(
        "/api/v1/payments/webhook/stripe",
        content=b'{}',
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 400
""",
}


DIRS = [
    "app",
    "app/api",
    "app/api/v1",
    "app/core",
    "app/integrations",
    "app/schemas",
    "app/services",
    "tests",
    "tests/api",
    "logs",
    "storage",
]


def ensure_init_files():
    init_paths = [
        "app/__init__.py",
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/core/__init__.py",
        "app/integrations/__init__.py",
        "app/schemas/__init__.py",
        "app/services/__init__.py",
        "tests/__init__.py",
        "tests/api/__init__.py",
    ]
    for rel in init_paths:
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("", encoding="utf-8")


def backup_file(path: Path):
    if path.exists():
        backup_target = BACKUP_DIR / path.relative_to(ROOT)
        backup_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_target)


def write_files():
    for rel_dir in DIRS:
        (ROOT / rel_dir).mkdir(parents=True, exist_ok=True)

    ensure_init_files()

    for rel_path, content in FILES.items():
        target = ROOT / rel_path
        backup_file(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def smoke_test():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    try:
        import fastapi  # noqa: F401
    except ModuleNotFoundError:
        print("ATTENTION: fastapi n'est pas installé dans cet interpréteur Python.")
        print(f"Interpréteur utilisé: {sys.executable}")
        print("Relance avec le même Python que celui utilisé pour tes dépendances.")
        print("Exemple Windows : py -3.9 repair_api.py")
        return

    module = importlib.import_module("app.main")
    app = getattr(module, "app", None)
    if app is None:
        raise RuntimeError("app.main a été importé, mais l'objet app est introuvable.")

    print("OK: import app.main réussi")
    print("OK: objet FastAPI app trouvé")


def main():
    print(f"Projet: {ROOT}")
    print(f"Python utilisé: {sys.executable}")
    print(f"Sauvegarde: {BACKUP_DIR}")
    write_files()
    smoke_test()
    print("Terminé.")
    print("Tu peux maintenant lancer :")
    print("  python -m pytest tests\\api -v")
    print("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()