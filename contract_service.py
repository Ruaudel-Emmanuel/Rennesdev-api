# app/services/contract_service.py
import uuid

from app.integrations.pdf_generator import PDFGenerator
from app.schemas.contracts import ContractCreate, ContractResponse


class ContractService:
    def __init__(self, pdf_generator: PDFGenerator):
        self.pdf_generator = pdf_generator

    async def create(self, payload: ContractCreate) -> ContractResponse:
        contract_id = f"contract_{uuid.uuid4().hex[:8]}"
        pdf_url = self.pdf_generator.create_fake_pdf(
            prefix=contract_id,
            content=f"Contrat pour {payload.customer_name} - {payload.service_name}",
        )
        return ContractResponse(contract_id=contract_id, pdf_url=pdf_url)