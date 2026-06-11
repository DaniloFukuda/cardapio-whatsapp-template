import json
import unicodedata
from dataclasses import dataclass
from typing import Any

from core.database import Database
from services.menu_service import MenuService, format_currency
from services.order_service import OrderService


MAIN_MENU = "main_menu"
AWAITING_MARMITA = "awaiting_marmita"
AWAITING_MEATS = "awaiting_meats"
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
            AWAITING_MARMITA: self._handle_marmita,
            AWAITING_MEATS: self._handle_meats,
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
            session["current_state"] = AWAITING_MARMITA
            self._save(session)
            return FlowResult(self.menu_service.format_daily_menu())
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

    def _handle_marmita(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        marmita_type = self.menu_service.get_marmita_type(text)
        if marmita_type is None:
            return FlowResult(
                f"Marmita inválida.\n\n{self.menu_service.format_daily_menu()}"
            )

        session["cart"]["context"] = {"marmita_type_id": marmita_type["id"]}
        session["current_state"] = AWAITING_MEATS
        self._save(session)
        return FlowResult(self.menu_service.format_meat_menu(marmita_type))

    def _handle_meats(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        marmita_type = self.menu_service.get_marmita_type(
            session["cart"]["context"].get("marmita_type_id", "")
        )
        if marmita_type is None:
            session["current_state"] = AWAITING_MARMITA
            session["cart"]["context"] = {}
            self._save(session)
            return FlowResult(
                "A marmita selecionada não está mais disponível.\n\n"
                f"{self.menu_service.format_daily_menu()}"
            )

        try:
            meats = self.menu_service.parse_meat_choices(text)
            self.menu_service.validate_meat_choices(marmita_type, meats)
        except ValueError as exc:
            return FlowResult(
                f"{exc}\n\n{self.menu_service.format_meat_menu(marmita_type)}"
            )

        session["cart"]["context"]["meat_ids"] = [meat["id"] for meat in meats]
        session["current_state"] = AWAITING_QUANTITY
        self._save(session)
        meat_names = " e ".join(meat["nome"] for meat in meats)
        return FlowResult(
            f"Carnes escolhidas: {meat_names}.\n\n"
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

        marmita_type = self.menu_service.get_marmita_type(
            session["cart"]["context"].get("marmita_type_id", "")
        )
        meats = [
            self.menu_service.get_meat(meat_id)
            for meat_id in session["cart"]["context"].get("meat_ids", [])
        ]
        if marmita_type is None or not meats or any(meat is None for meat in meats):
            session["current_state"] = AWAITING_MARMITA
            session["cart"]["context"] = {}
            self._save(session)
            return FlowResult(
                "O cardápio do dia mudou. Escolha sua marmita novamente.\n\n"
                f"{self.menu_service.format_daily_menu()}"
            )

        session["cart"] = self.order_service.add_item(
            session["cart"], marmita_type, meats, quantity
        )
        session["current_state"] = AFTER_ADD
        self._save(session)
        added_item = next(
            item
            for item in session["cart"]["items"]
            if item["marmita_type_id"] == marmita_type["id"]
            and {meat["id"] for meat in item["meats"]}
            == {meat["id"] for meat in meats}
        )
        return FlowResult(
            "Adicionado ao carrinho:\n\n"
            f"{self.order_service.format_item({**added_item, 'quantity': quantity})}\n\n"
            f"{self._after_add_options()}"
        )

    def _handle_after_add(
        self, session: dict[str, Any], text: str
    ) -> FlowResult:
        if text == "1":
            session["current_state"] = AWAITING_MARMITA
            self._save(session)
            return FlowResult(self.menu_service.format_daily_menu())
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
