import json
import unicodedata
from dataclasses import dataclass
from typing import Any

from core.database import Database
from services.menu_service import MenuService, format_currency
from services.order_service import OrderService


MAIN_MENU = "main_menu"
AWAITING_CATEGORY = "awaiting_category"
AWAITING_PRODUCT = "awaiting_product"
AWAITING_QUANTITY = "awaiting_quantity"
AFTER_ADD = "after_add"
AWAITING_NAME = "awaiting_name"
AWAITING_DELIVERY_TYPE = "awaiting_delivery_type"
AWAITING_ADDRESS = "awaiting_address"
AWAITING_PAYMENT = "awaiting_payment"
AWAITING_NOTES = "awaiting_notes"
AWAITING_CONFIRMATION = "awaiting_confirmation"

START_COMMANDS = {"oi", "ola", "menu", "cardapio", "pedido", "comecar", "iniciar"}


@dataclass
class FlowResult:
    reply: str
    order: dict[str, Any] | None = None


class SessionService:
    def __init__(
        self,
        database: Database,
        menu_service: MenuService,
        order_service: OrderService,
        restaurant_name: str,
    ):
        self.database = database
        self.menu_service = menu_service
        self.order_service = order_service
        self.restaurant_name = restaurant_name

    def get_or_create_session(self, customer_phone: str) -> dict[str, Any]:
        self.database.execute(
            """
            INSERT OR IGNORE INTO customer_sessions (
                customer_phone, current_state, cart_json
            ) VALUES (?, ?, ?)
            """,
            (
                customer_phone,
                MAIN_MENU,
                json.dumps(self.order_service.empty_cart(), ensure_ascii=False),
            ),
        )
        row = self.database.fetch_one(
            "SELECT * FROM customer_sessions WHERE customer_phone = ?",
            (customer_phone,),
        )
        return self._deserialize_session(row)

    def handle_message(self, customer_phone: str, message: str) -> FlowResult:
        session = self.get_or_create_session(customer_phone)
        text = message.strip()
        normalized = normalize_text(text)

        if normalized in START_COMMANDS:
            session["current_state"] = MAIN_MENU
            session["cart"]["context"] = {}
            self._save(session)
            return FlowResult(self._main_menu(greeting=True))

        if text == "0":
            self._reset(session)
            return FlowResult(
                "Pedido cancelado. Quando quiser começar novamente, digite menu."
            )

        state = session["current_state"]
        handlers = {
            MAIN_MENU: self._handle_main_menu,
            AWAITING_CATEGORY: self._handle_category,
            AWAITING_PRODUCT: self._handle_product,
            AWAITING_QUANTITY: self._handle_quantity,
            AFTER_ADD: self._handle_after_add,
            AWAITING_NAME: self._handle_name,
            AWAITING_DELIVERY_TYPE: self._handle_delivery_type,
            AWAITING_ADDRESS: self._handle_address,
            AWAITING_PAYMENT: self._handle_payment,
            AWAITING_NOTES: self._handle_notes,
            AWAITING_CONFIRMATION: self._handle_confirmation,
        }
        handler = handlers.get(state, self._handle_main_menu)
        return handler(session, text)

    def _handle_main_menu(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        if text == "1":
            session["current_state"] = AWAITING_CATEGORY
            self._save(session)
            return FlowResult(self.menu_service.format_categories_menu())
        if text == "2":
            session["current_state"] = AFTER_ADD
            self._save(session)
            return FlowResult(
                f"{self.order_service.format_cart(session['cart'])}\n\n"
                f"{self._after_add_options()}"
            )
        if text == "3":
            return self._start_checkout(session)
        return FlowResult(
            f"Opção inválida.\n\n{self._main_menu(greeting=False)}"
        )

    def _handle_category(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        categories = self.menu_service.list_categories()
        index = parse_choice(text, len(categories))
        if index is None:
            return FlowResult(
                f"Categoria inválida.\n\n{self.menu_service.format_categories_menu()}"
            )

        category = categories[index]
        session["cart"]["context"] = {"category_id": category["id"]}
        session["current_state"] = AWAITING_PRODUCT
        self._save(session)
        return FlowResult(self.menu_service.format_products_menu(category["id"]))

    def _handle_product(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        category_id = session["cart"]["context"].get("category_id")
        products = self.menu_service.list_products_by_category(category_id)
        index = parse_choice(text, len(products))
        if index is None:
            return FlowResult(
                f"Produto inválido.\n\n"
                f"{self.menu_service.format_products_menu(category_id)}"
            )

        product = products[index]
        session["cart"]["context"]["product_id"] = product["id"]
        session["current_state"] = AWAITING_QUANTITY
        self._save(session)
        return FlowResult(
            f"Você escolheu {product['nome']} - "
            f"{format_currency(product['preco'])}.\n\n"
            "Digite a quantidade desejada."
        )

    def _handle_quantity(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        try:
            quantity = int(text)
        except ValueError:
            quantity = 0
        if quantity < 1 or quantity > 99:
            return FlowResult("Digite uma quantidade válida entre 1 e 99.")

        product_id = session["cart"]["context"].get("product_id")
        product = self.menu_service.get_product(product_id)
        if not product:
            session["current_state"] = AWAITING_CATEGORY
            session["cart"]["context"] = {}
            self._save(session)
            return FlowResult(
                "O produto não está mais disponível.\n\n"
                f"{self.menu_service.format_categories_menu()}"
            )

        session["cart"] = self.order_service.add_item(
            session["cart"], product, quantity
        )
        session["current_state"] = AFTER_ADD
        self._save(session)
        return FlowResult(
            "Adicionado ao carrinho:\n"
            f"{quantity}x {product['nome']}\n\n"
            f"{self._after_add_options()}"
        )

    def _handle_after_add(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        if text == "1":
            session["current_state"] = AWAITING_CATEGORY
            self._save(session)
            return FlowResult(self.menu_service.format_categories_menu())
        if text == "2":
            return FlowResult(
                f"{self.order_service.format_cart(session['cart'])}\n\n"
                f"{self._after_add_options()}"
            )
        if text == "3":
            return self._start_checkout(session)
        return FlowResult(f"Opção inválida.\n\n{self._after_add_options()}")

    def _start_checkout(self, session: dict[str, Any]) -> FlowResult:
        if not session["cart"]["items"]:
            session["current_state"] = MAIN_MENU
            self._save(session)
            return FlowResult(
                "Seu carrinho está vazio.\n\n"
                f"{self._main_menu(greeting=False)}"
            )
        session["current_state"] = AWAITING_NAME
        self._save(session)
        return FlowResult("Para finalizar, qual é o seu nome?")

    def _handle_name(self, session: dict[str, Any], text: str) -> FlowResult:
        if len(text) < 2:
            return FlowResult("Digite um nome válido para identificar o pedido.")
        session["customer_name"] = text[:120]
        session["current_state"] = AWAITING_DELIVERY_TYPE
        self._save(session)
        return FlowResult(
            "Como você quer receber?\n\n1 - Entrega\n2 - Retirada"
        )

    def _handle_delivery_type(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        if text not in {"1", "2"}:
            return FlowResult("Digite 1 para Entrega ou 2 para Retirada.")
        session["delivery_type"] = "entrega" if text == "1" else "retirada"
        if session["delivery_type"] == "entrega":
            session["current_state"] = AWAITING_ADDRESS
            self._save(session)
            return FlowResult(
                "Digite o endereço completo para entrega, com número e bairro."
            )
        session["address"] = None
        session["current_state"] = AWAITING_PAYMENT
        self._save(session)
        return FlowResult(self._payment_options())

    def _handle_address(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        if len(text) < 5:
            return FlowResult("Digite um endereço mais completo.")
        session["address"] = text[:300]
        session["current_state"] = AWAITING_PAYMENT
        self._save(session)
        return FlowResult(self._payment_options())

    def _handle_payment(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        methods = {"1": "pix", "2": "dinheiro", "3": "cartão"}
        if text not in methods:
            return FlowResult(self._payment_options(invalid=True))
        session["payment_method"] = methods[text]
        session["current_state"] = AWAITING_NOTES
        self._save(session)
        return FlowResult(
            'Deseja adicionar alguma observação? Digite a observação ou "não".'
        )

    def _handle_notes(self, session: dict[str, Any], text: str) -> FlowResult:
        session["notes"] = (
            None if normalize_text(text) in {"nao", "sem", "nenhuma"} else text[:500]
        )
        session["current_state"] = AWAITING_CONFIRMATION
        self._save(session)
        return FlowResult(self.order_service.format_confirmation(session))

    def _handle_confirmation(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        if text == "1":
            order = self.order_service.create_order(session)
            self._reset(session)
            return FlowResult(
                "Pedido confirmado! ✅\n\n"
                f"Número do pedido: {order['order_number']}\n"
                f"Total: {format_currency(order['total'])}\n\n"
                "O restaurante já recebeu seu pedido e vai te chamar por aqui "
                "se precisar confirmar alguma informação.",
                order=order,
            )
        if text == "2":
            session["current_state"] = MAIN_MENU
            self._save(session)
            return FlowResult(
                "Você pode continuar comprando ou revisar o carrinho.\n\n"
                f"{self._main_menu(greeting=False)}"
            )
        return FlowResult(
            "Digite 1 para confirmar, 2 para alterar ou 0 para cancelar."
        )

    def _save(self, session: dict[str, Any]) -> None:
        self.database.execute(
            """
            UPDATE customer_sessions
            SET current_state = ?, cart_json = ?, customer_name = ?,
                delivery_type = ?, address = ?, payment_method = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE customer_phone = ?
            """,
            (
                session["current_state"],
                json.dumps(session["cart"], ensure_ascii=False),
                session.get("customer_name"),
                session.get("delivery_type"),
                session.get("address"),
                session.get("payment_method"),
                session.get("notes"),
                session["customer_phone"],
            ),
        )

    def _reset(self, session: dict[str, Any]) -> None:
        session.update(
            {
                "current_state": MAIN_MENU,
                "cart": self.order_service.empty_cart(),
                "customer_name": None,
                "delivery_type": None,
                "address": None,
                "payment_method": None,
                "notes": None,
            }
        )
        self._save(session)

    @staticmethod
    def _deserialize_session(row: dict[str, Any]) -> dict[str, Any]:
        session = dict(row)
        session["cart"] = json.loads(session.pop("cart_json"))
        return session

    def _main_menu(self, greeting: bool) -> str:
        lines = []
        if greeting:
            lines.extend(
                [f"Olá! Bem-vindo ao {self.restaurant_name} 🍽️", ""]
            )
        lines.extend(
            [
                "Digite uma opção:",
                "",
                "1 - Ver cardápio",
                "2 - Ver carrinho",
                "3 - Finalizar pedido",
                "0 - Cancelar pedido",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _after_add_options() -> str:
        return "\n".join(
            [
                "Digite:",
                "1 - Continuar comprando",
                "2 - Ver carrinho",
                "3 - Finalizar pedido",
                "0 - Cancelar",
            ]
        )

    @staticmethod
    def _payment_options(invalid: bool = False) -> str:
        prefix = "Opção inválida.\n\n" if invalid else ""
        return (
            f"{prefix}Qual será a forma de pagamento?\n\n"
            "1 - Pix\n2 - Dinheiro\n3 - Cartão"
        )


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(without_accents.strip().split())


def parse_choice(value: str, total_options: int) -> int | None:
    try:
        index = int(value) - 1
    except ValueError:
        return None
    return index if 0 <= index < total_options else None
