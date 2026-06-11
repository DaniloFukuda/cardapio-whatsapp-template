import json
from typing import Any

from core.database import Database
from services.menu_service import format_currency


class OrderService:
    def __init__(self, database: Database, delivery_fee: float = 5.0):
        self.database = database
        self.delivery_fee = delivery_fee

    @staticmethod
    def empty_cart() -> dict[str, Any]:
        return {"items": [], "context": {}}

    def add_item(
        self, cart: dict[str, Any], product: dict[str, Any], quantity: int
    ) -> dict[str, Any]:
        if quantity < 1:
            raise ValueError("A quantidade deve ser maior que zero.")

        normalized = {
            "items": list(cart.get("items", [])),
            "context": dict(cart.get("context", {})),
        }
        existing = next(
            (item for item in normalized["items"] if item["product_id"] == product["id"]),
            None,
        )
        if existing:
            existing["quantity"] += quantity
        else:
            normalized["items"].append(
                {
                    "product_id": product["id"],
                    "name": product["nome"],
                    "unit_price": float(product["preco"]),
                    "quantity": quantity,
                }
            )
        normalized["context"] = {}
        return normalized

    @staticmethod
    def calculate_subtotal(items: list[dict[str, Any]]) -> float:
        return round(
            sum(float(item["unit_price"]) * int(item["quantity"]) for item in items),
            2,
        )

    def calculate_totals(
        self, items: list[dict[str, Any]], delivery_type: str
    ) -> dict[str, float]:
        subtotal = self.calculate_subtotal(items)
        delivery_fee = self.delivery_fee if delivery_type == "entrega" else 0.0
        return {
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "total": round(subtotal + delivery_fee, 2),
        }

    def format_cart(self, cart: dict[str, Any]) -> str:
        items = cart.get("items", [])
        if not items:
            return "Seu carrinho está vazio."

        lines = ["Seu carrinho:", ""]
        for item in items:
            item_total = float(item["unit_price"]) * int(item["quantity"])
            lines.append(
                f"- {item['quantity']}x {item['name']} - {format_currency(item_total)}"
            )
        lines.extend(
            ["", f"Subtotal: {format_currency(self.calculate_subtotal(items))}"]
        )
        return "\n".join(lines)

    def format_confirmation(self, session: dict[str, Any]) -> str:
        cart = session["cart"]
        totals = self.calculate_totals(cart["items"], session["delivery_type"])
        lines = [
            "Confirme seu pedido:",
            "",
            f"Cliente: {session['customer_name']}",
            f"Tipo: {session['delivery_type'].title()}",
        ]
        if session["delivery_type"] == "entrega":
            lines.append(f"Endereço: {session['address']}")
        lines.extend(
            [
                f"Pagamento: {session['payment_method'].title()}",
                "",
                "Itens:",
            ]
        )
        for item in cart["items"]:
            item_total = float(item["unit_price"]) * int(item["quantity"])
            lines.append(
                f"{item['quantity']}x {item['name']} - {format_currency(item_total)}"
            )
        lines.extend(
            [
                "",
                f"Subtotal: {format_currency(totals['subtotal'])}",
                f"Taxa de entrega: {format_currency(totals['delivery_fee'])}",
                f"Total: {format_currency(totals['total'])}",
                "",
                "Digite:",
                "1 - Confirmar pedido",
                "2 - Alterar pedido",
                "0 - Cancelar",
            ]
        )
        return "\n".join(lines)

    def create_order(self, session: dict[str, Any]) -> dict[str, Any]:
        items = session["cart"]["items"]
        if not items:
            raise ValueError("Não é possível confirmar um carrinho vazio.")

        totals = self.calculate_totals(items, session["delivery_type"])
        with self.database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            next_id = connection.execute(
                "SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM orders"
            ).fetchone()["next_id"]
            order_number = f"PED-{next_id:06d}"
            cursor = connection.execute(
                """
                INSERT INTO orders (
                    order_number, customer_phone, customer_name, items_json,
                    subtotal, delivery_fee, total, delivery_type, address,
                    payment_method, notes, status, staff_notification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'confirmed', 'pending')
                """,
                (
                    order_number,
                    session["customer_phone"],
                    session.get("customer_name"),
                    json.dumps(items, ensure_ascii=False),
                    totals["subtotal"],
                    totals["delivery_fee"],
                    totals["total"],
                    session["delivery_type"],
                    session.get("address"),
                    session["payment_method"],
                    session.get("notes"),
                ),
            )
            order_id = cursor.lastrowid

        return self.get_order(order_id)

    def get_order(self, order_id: int) -> dict[str, Any] | None:
        row = self.database.fetch_one("SELECT * FROM orders WHERE id = ?", (order_id,))
        return self._deserialize_order(row) if row else None

    def list_orders(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = self.database.fetch_all(
            "SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [self._deserialize_order(row) for row in rows]

    @staticmethod
    def _deserialize_order(row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        result["items"] = json.loads(result.pop("items_json"))
        return result

    def update_staff_notification(
        self, order_id: int, status: str, error: str | None = None
    ) -> None:
        self.database.execute(
            """
            UPDATE orders
            SET staff_notification_status = ?, staff_notification_error = ?
            WHERE id = ?
            """,
            (status, error, order_id),
        )

    def format_staff_message(self, order: dict[str, Any]) -> str:
        lines = [
            f"🔔 NOVO PEDIDO - {order['order_number']}",
            "",
            f"Cliente: {order.get('customer_name') or 'Não informado'}",
            f"WhatsApp: {order['customer_phone']}",
            "",
            f"Tipo: {order['delivery_type'].title()}",
        ]
        if order["delivery_type"] == "entrega":
            lines.append(f"Endereço: {order.get('address') or 'Não informado'}")
        lines.extend(
            [
                f"Pagamento: {order['payment_method'].title()}",
                "",
                "Itens:",
            ]
        )
        for item in order["items"]:
            item_total = float(item["unit_price"]) * int(item["quantity"])
            lines.append(
                f"- {item['quantity']}x {item['name']} - {format_currency(item_total)}"
            )
        lines.extend(
            [
                "",
                f"Subtotal: {format_currency(order['subtotal'])}",
                f"Taxa de entrega: {format_currency(order['delivery_fee'])}",
                f"Total: {format_currency(order['total'])}",
                "",
                "Observações:",
                order.get("notes") or "Sem observações.",
                "",
                "Responder o cliente pelo WhatsApp dele para confirmar preparo/entrega.",
            ]
        )
        return "\n".join(lines)
