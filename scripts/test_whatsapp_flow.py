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


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        database_path = Path(temp_dir) / "flow.db"
        database = Database(f"sqlite:///{database_path.as_posix()}")
        database.init_db()
        menu = MenuService()
        orders = OrderService(database, delivery_fee=5.0)
        sessions = SessionService(database, menu, orders, "Sabor Brasileiro")

        messages = [
            "oi",
            "1",
            "1",
            "2",
            "2",
            "3",
            "João",
            "2",
            "1",
            "não",
            "1",
        ]
        result = None
        for message in messages:
            result = sessions.handle_message("5561999999999", message)
            print(f"\nCLIENTE: {message}\nBOT: {result.reply}")

        assert result is not None and result.order is not None
        assert result.order["order_number"] == "PED-000001"
        assert result.order["total"] == 44.0
        assert len(orders.list_orders()) == 1
        print("\nFluxo simulado concluído com sucesso.")


if __name__ == "__main__":
    main()
