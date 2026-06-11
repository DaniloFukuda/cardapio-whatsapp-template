import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from config.settings import get_settings
from core.database import Database
from services.menu_service import MenuService
from services.order_service import OrderService
from services.session_service import SessionService
from services.whatsapp_client import WhatsAppClient, WhatsAppClientError

logger = logging.getLogger(__name__)
settings = get_settings()
database = Database(settings.database_url)
menu_service = MenuService()
order_service = OrderService(database, settings.delivery_fee)
session_service = SessionService(
    database, menu_service, order_service, settings.restaurant_name
)
whatsapp_client = WhatsAppClient(settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    database.init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, Any]:
    database_status = database.health()
    return {
        "status": "ok" if database_status["status"] == "ok" else "degraded",
        "app": settings.app_name,
        "environment": settings.environment,
        "database": database_status,
    }


@app.get("/webhook/whatsapp", response_class=PlainTextResponse)
def verify_whatsapp_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
) -> PlainTextResponse:
    if (
        hub_mode == "subscribe"
        and hub_verify_token == settings.whatsapp_verify_token
        and hub_challenge is not None
    ):
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Token de verificação inválido.")


@app.post("/webhook/whatsapp")
async def receive_whatsapp_webhook(request: Request) -> JSONResponse:
    payload = await request.json()
    messages = extract_messages(payload)

    for message in messages:
        message_id = message.get("id")
        from_number = message.get("from")
        if not message_id or not from_number:
            continue

        message_type = message.get("type")
        text = (
            message.get("text", {}).get("body")
            if message_type == "text"
            else None
        )
        is_new = database.save_incoming_message(
            message_id, from_number, text, payload
        )
        if not is_new:
            continue

        if message_type != "text":
            await send_safely(
                from_number,
                "Por enquanto, este atendimento aceita apenas mensagens de texto.",
            )
            continue

        result = session_service.handle_message(from_number, text or "")
        await send_safely(from_number, result.reply)
        if result.order:
            await notify_staff(result.order)

    return JSONResponse({"status": "received"})


@app.get("/pedidos")
def list_orders(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
    orders = order_service.list_orders(limit)
    return {"count": len(orders), "orders": orders}


@app.get("/pedidos/{pedido_id}")
def get_order(pedido_id: int) -> dict[str, Any]:
    order = order_service.get_order(pedido_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return order


def extract_messages(payload: dict[str, Any]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            value_messages = value.get("messages", [])
            if isinstance(value_messages, list):
                messages.extend(
                    message for message in value_messages if isinstance(message, dict)
                )
    return messages


async def notify_staff(order: dict[str, Any]) -> None:
    try:
        await whatsapp_client.send_text(
            settings.restaurant_staff_whatsapp_number,
            order_service.format_staff_message(order),
        )
        order_service.update_staff_notification(order["id"], "sent")
    except WhatsAppClientError as exc:
        error = str(exc)[:1000]
        order_service.update_staff_notification(order["id"], "failed", error)
        logger.warning(
            "Falha ao notificar equipe sobre pedido %s: %s",
            order["order_number"],
            error,
        )


async def send_safely(to: str, body: str) -> None:
    try:
        await whatsapp_client.send_text(to, body)
    except WhatsAppClientError as exc:
        logger.warning("Falha ao responder mensagem do WhatsApp: %s", exc)
