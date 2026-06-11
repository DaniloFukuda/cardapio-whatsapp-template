from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.database import Database
from services.menu_service import MenuService
from services.order_service import OrderService
from services.session_service import SessionService


@pytest.fixture
def database(tmp_path: Path) -> Database:
    db = Database(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    db.init_db()
    return db


@pytest.fixture
def menu_service() -> MenuService:
    return MenuService()


@pytest.fixture
def order_service(database: Database) -> OrderService:
    return OrderService(database, delivery_fee=5.0)


@pytest.fixture
def session_service(
    database: Database,
    menu_service: MenuService,
    order_service: OrderService,
) -> SessionService:
    return SessionService(
        database, menu_service, order_service, "Restaurante de Teste"
    )
