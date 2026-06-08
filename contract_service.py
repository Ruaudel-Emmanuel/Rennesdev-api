import uuid

from app.schemas.contracts import ContractCreate, ContractResponse


class ContractService:
    async def create_contract(self, payload: ContractCreate) -> ContractResponse:
        contract_id = "contract_" + uuid.uuid4().hex[:12]
        return ContractResponse(
            contract_id=contract_id,
            pdf_url="storage/%s.pdf" % contract_id,
        )