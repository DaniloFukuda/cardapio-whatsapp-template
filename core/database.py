import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


SCHEMA = """
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wa_message_id TEXT NOT NULL UNIQUE,
    from_number TEXT NOT NULL,
    message_text TEXT,
    raw_payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customer_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_phone TEXT NOT NULL UNIQUE,
    current_state TEXT NOT NULL,
    cart_json TEXT NOT NULL DEFAULT '{"items":[],"context":{}}',
    customer_name TEXT,
    delivery_type TEXT,
    address TEXT,
    payment_method TEXT,
    notes TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT NOT NULL UNIQUE,
    customer_phone TEXT NOT NULL,
    customer_name TEXT,
    items_json TEXT NOT NULL,
    subtotal REAL NOT NULL,
    delivery_fee REAL NOT NULL,
    total REAL NOT NULL,
    delivery_type TEXT NOT NULL,
    address TEXT,
    payment_method TEXT NOT NULL,
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'confirmed',
    staff_notification_status TEXT NOT NULL DEFAULT 'pending',
    staff_notification_error TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_created_at
ON whatsapp_messages(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_orders_created_at
ON orders(created_at DESC);
"""


class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.path = self._path_from_url(database_url)

    @staticmethod
    def _path_from_url(database_url: str) -> str:
        prefix = "sqlite:///"
        if not database_url.startswith(prefix):
            raise ValueError("Apenas DATABASE_URL SQLite é suportada nesta versão.")

        path = database_url[len(prefix) :]
        if path == ":memory:":
            return path
        return str(Path(path).expanduser().resolve())

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def init_db(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def health(self) -> dict[str, Any]:
        try:
            with self.connect() as connection:
                connection.execute("SELECT 1").fetchone()
            return {"status": "ok", "engine": "sqlite"}
        except sqlite3.Error as exc:
            return {"status": "error", "engine": "sqlite", "detail": str(exc)}

    def save_incoming_message(
        self,
        wa_message_id: str,
        from_number: str,
        message_text: str | None,
        raw_payload: dict[str, Any],
    ) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO whatsapp_messages (
                    wa_message_id, from_number, message_text, raw_payload_json
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    wa_message_id,
                    from_number,
                    message_text,
                    json.dumps(raw_payload, ensure_ascii=False),
                ),
            )
            return cursor.rowcount == 1

    def fetch_all(
        self, query: str, parameters: tuple[Any, ...] = ()
    ) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]

    def fetch_one(
        self, query: str, parameters: tuple[Any, ...] = ()
    ) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(query, parameters).fetchone()
        return dict(row) if row else None

    def execute(self, query: str, parameters: tuple[Any, ...] = ()) -> int:
        with self.connect() as connection:
            cursor = connection.execute(query, parameters)
            return cursor.lastrowid
