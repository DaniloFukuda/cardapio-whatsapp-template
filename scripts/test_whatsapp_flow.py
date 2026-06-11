from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.database import Database
from services.menu_service import MenuService
from services.order_service import OrderService
from services.session_service import SessionService


def simulate(
    sessions: SessionService, phone: str, messages: list[str], expected_total: float
):
    result = None
    for message in messages:
        result = sessions.handle_message(phone, message)
        print(f"\nCLIENTE: {message}\nBOT: {result.reply}")

    assert result is not None and result.order is not None
    assert result.order["total"] == expected_total
    return result.order


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        database_path = Path(temp_dir) / "flow.db"
        database = Database(f"sqlite:///{database_path.as_posix()}")
        database.init_db()
        menu = MenuService()
        orders = OrderService(database, delivery_fee=5.0)
        sessions = SessionService(database, menu, orders, "Sabor Brasileiro")

        small = simulate(
            sessions,
            "5561999999991",
            ["oi", "1", "1", "1", "2", "3", "Ana", "2", "1", "não", "1"],
            42.0,
        )
        assert small["items"][0]["name"] == "Marmita pequena"
        assert small["items"][0]["meats"][0]["name"] == "Churrasco"

        two_meats = simulate(
            sessions,
            "5561999999992",
            [
                "menu",
                "1",
                "2",
                "1 e 2",
                "2",
                "3",
                "João",
                "2",
                "1",
                "não",
                "1",
            ],
            46.0,
        )
        assert [meat["name"] for meat in two_meats["items"][0]["meats"]] == [
            "Churrasco",
            "Frango",
        ]
        assert len(orders.list_orders()) == 2
        print("\nFluxos de marmita pequena e de 2 carnes concluídos com sucesso.")


if __name__ == "__main__":
    main()
