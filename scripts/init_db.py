from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config.settings import get_settings
from core.database import Database


def main() -> None:
    settings = get_settings()
    database = Database(settings.database_url)
    database.init_db()
    print(f"Banco inicializado com sucesso: {database.path}")


if __name__ == "__main__":
    main()
