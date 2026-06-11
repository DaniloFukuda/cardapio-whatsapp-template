import json
from pathlib import Path
from typing import Any


class MenuService:
    def __init__(self, menu_path: str | Path | None = None):
        default_path = Path(__file__).resolve().parents[1] / "data" / "cardapio.json"
        self.menu_path = Path(menu_path) if menu_path else default_path
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        with self.menu_path.open(encoding="utf-8") as menu_file:
            data = json.load(menu_file)

        if not isinstance(data.get("categorias"), list):
            raise ValueError("O cardápio precisa conter uma lista de categorias.")
        return data

    def reload(self) -> None:
        self._data = self._load()

    def list_categories(self) -> list[dict[str, Any]]:
        return [dict(category) for category in self._data["categorias"]]

    def get_category(self, category_id: str) -> dict[str, Any] | None:
        return next(
            (
                dict(category)
                for category in self._data["categorias"]
                if category["id"] == category_id
            ),
            None,
        )

    def list_products_by_category(self, category_id: str) -> list[dict[str, Any]]:
        category = self.get_category(category_id)
        return [dict(product) for product in category["produtos"]] if category else []

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        for category in self._data["categorias"]:
            for product in category["produtos"]:
                if product["id"] == product_id:
                    return {
                        **product,
                        "categoria_id": category["id"],
                        "categoria_nome": category["nome"],
                    }
        return None

    def format_categories_menu(self) -> str:
        lines = ["Cardápio:", ""]
        lines.extend(
            f"{index} - {category['nome']}"
            for index, category in enumerate(self.list_categories(), start=1)
        )
        lines.extend(["", "Digite o número da categoria."])
        return "\n".join(lines)

    def format_products_menu(self, category_id: str) -> str:
        category = self.get_category(category_id)
        if not category:
            raise ValueError("Categoria não encontrada.")

        lines = [f"{category['nome']}:", ""]
        lines.extend(
            f"{index} - {product['nome']} - {format_currency(product['preco'])}"
            for index, product in enumerate(category["produtos"], start=1)
        )
        lines.extend(["", "Digite o número do produto."])
        return "\n".join(lines)


def format_currency(value: float) -> str:
    formatted = f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"
