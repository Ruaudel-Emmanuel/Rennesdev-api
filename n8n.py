# app/integrations/n8n.py
import httpx


class N8NClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def post_webhook(self, webhook_url: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
            if response.content:
                return response.json()
            return {"success": True}

    async def send_lead(self, webhook_url: str, payload: dict) -> dict:
        return await self.post_webhook(webhook_url, payload)

    async def send_quote(self, webhook_url: str, payload: dict) -> dict:
        return await self.post_webhook(webhook_url, payload)

    async def send_order(self, webhook_url: str, payload: dict) -> dict:
        return await self.post_webhook(webhook_url, payload)