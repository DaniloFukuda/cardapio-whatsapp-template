from fastapi.testclient import TestClient

import web_app
from core.database import Database
from services.menu_service import MenuService
from services.order_service import OrderService
from services.session_service import SessionService


class FakeWhatsAppClient:
    def __init__(self):
        self.sent = []

    async def send_text(self, to, body):
        self.sent.append({"to": to, "body": body})
        return {"messages": [{"id": "wamid.out"}]}


def configure_test_app(monkeypatch, tmp_path):
    database = Database(f"sqlite:///{(tmp_path / 'webhook.db').as_posix()}")
    menu = MenuService()
    orders = OrderService(database, delivery_fee=5.0)
    sessions = SessionService(database, menu, orders, "Restaurante de Teste")
    whatsapp = FakeWhatsAppClient()

    monkeypatch.setattr(web_app, "database", database)
    monkeypatch.setattr(web_app, "menu_service", menu)
    monkeypatch.setattr(web_app, "order_service", orders)
    monkeypatch.setattr(web_app, "session_service", sessions)
    monkeypatch.setattr(web_app, "whatsapp_client", whatsapp)
    monkeypatch.setattr(web_app.settings, "admin_api_key", "admin-test-key")
    return database, whatsapp


def test_health_is_public(monkeypatch, tmp_path):
    configure_test_app(monkeypatch, tmp_path)

    with TestClient(web_app.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_orders_require_admin_api_key(monkeypatch, tmp_path):
    configure_test_app(monkeypatch, tmp_path)

    with TestClient(web_app.app) as client:
        missing = client.get("/pedidos")
        invalid = client.get(
            "/pedidos", headers={"X-Admin-API-Key": "wrong-key"}
        )
        authorized = client.get(
            "/pedidos", headers={"X-Admin-API-Key": "admin-test-key"}
        )
        detail_missing = client.get("/pedidos/1")
        detail_authorized = client.get(
            "/pedidos/1", headers={"X-Admin-API-Key": "admin-test-key"}
        )

    assert missing.status_code == 401
    assert invalid.status_code == 401
    assert authorized.status_code == 200
    assert authorized.json() == {"count": 0, "orders": []}
    assert detail_missing.status_code == 401
    assert detail_authorized.status_code == 404


def test_webhook_verification(monkeypatch, tmp_path):
    configure_test_app(monkeypatch, tmp_path)
    with TestClient(web_app.app) as client:
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": web_app.settings.whatsapp_verify_token,
                "hub.challenge": "12345",
            },
        )
        forbidden = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "invalid",
                "hub.challenge": "12345",
            },
        )

    assert response.status_code == 200
    assert response.text == "12345"
    assert forbidden.status_code == 403


def test_webhook_deduplicates_messages(monkeypatch, tmp_path):
    database, whatsapp = configure_test_app(monkeypatch, tmp_path)
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.in.1",
                                    "from": "5561999999999",
                                    "type": "text",
                                    "text": {"body": "oi"},
                                }
                            ]
                        }
                    }
                ]
            }
        ],
    }

    with TestClient(web_app.app) as client:
        first = client.post("/webhook/whatsapp", json=payload)
        duplicate = client.post("/webhook/whatsapp", json=payload)

    messages = database.fetch_all("SELECT * FROM whatsapp_messages")
    assert first.status_code == 200
    assert duplicate.status_code == 200
    assert len(messages) == 1
    assert len(whatsapp.sent) == 1
    assert "Bem-vindo" in whatsapp.sent[0]["body"]
