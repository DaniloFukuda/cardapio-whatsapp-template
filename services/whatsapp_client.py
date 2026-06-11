from typing import Any

import httpx

from config.settings import Settings


class WhatsAppClientError(RuntimeError):
    pass


class WhatsAppClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def send_text(self, to: str, body: str) -> dict[str, Any]:
        if (
            not self.settings.whatsapp_access_token
            or not self.settings.whatsapp_phone_number_id
        ):
            raise WhatsAppClientError(
                "Credenciais da WhatsApp Cloud API não configuradas."
            )

        url = (
            "https://graph.facebook.com/"
            f"{self.settings.whatsapp_graph_api_version}/"
            f"{self.settings.whatsapp_phone_number_id}/messages"
        )
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        }

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500]
            raise WhatsAppClientError(
                f"Meta Graph API retornou HTTP {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise WhatsAppClientError(
                f"Falha de rede ao enviar mensagem para a Meta: {exc}"
            ) from exc
