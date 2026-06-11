import json
import re
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

        if not isinstance(data.get("tipos_marmita"), list):
            raise ValueError("O cardápio precisa conter tipos de marmita.")
        if not isinstance(data.get("carnes_do_dia"), list):
            raise ValueError("O cardápio precisa conter carnes do dia.")

        meats = data["carnes_do_dia"]
        barbecue = next((meat for meat in meats if meat["id"] == "churrasco"), None)
        if barbecue is None:
            meats.insert(0, {"id": "churrasco", "nome": "Churrasco", "fixo": True})
        else:
            barbecue["fixo"] = True
        return data

    def reload(self) -> None:
        self._data = self._load()

    def list_marmita_types(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._data["tipos_marmita"]]

    def list_daily_meats(self) -> list[dict[str, Any]]:
        return [dict(meat) for meat in self._data["carnes_do_dia"]]

    def get_marmita_type(self, value: str | int) -> dict[str, Any] | None:
        return self._find_by_number_or_id(self.list_marmita_types(), value)

    def get_meat(self, value: str | int) -> dict[str, Any] | None:
        return self._find_by_number_or_id(self.list_daily_meats(), value)

    def parse_meat_choices(self, value: str) -> list[dict[str, Any]]:
        choices = [
            part
            for part in re.split(r"\s*(?:,|/|\be\b|\s+)\s*", value.strip())
            if part
        ]
        meats = [self.get_meat(choice) for choice in choices]
        if not choices or any(meat is None for meat in meats):
            raise ValueError("Escolha apenas carnes disponíveis no cardápio de hoje.")
        if len({meat["id"] for meat in meats}) != len(meats):
            raise ValueError("Não repita a mesma carne no item.")
        return meats

    def validate_meat_choices(
        self, marmita_type: dict[str, Any], meats: list[dict[str, Any]]
    ) -> None:
        expected = int(marmita_type["quantidade_carnes"])
        if len(meats) != expected:
            label = "carne" if expected == 1 else "carnes"
            raise ValueError(f"Escolha exatamente {expected} {label}.")
        if len({meat["id"] for meat in meats}) != len(meats):
            raise ValueError("Não repita a mesma carne no item.")

    def format_daily_menu(self) -> str:
        lines = ["Cardápio de hoje 🍽️", "", "Marmitas:"]
        for index, item in enumerate(self.list_marmita_types(), start=1):
            count = item["quantidade_carnes"]
            label = "carne" if count == 1 else "carnes"
            count_text = f"{count} {label}"
            detail = "" if count_text in item["nome"].casefold() else f" - {count_text}"
            lines.append(
                f"{index} - {item['nome']}{detail} - "
                f"{format_currency(item['preco'])}"
            )
        lines.extend(["", "Carnes disponíveis hoje:"])
        lines.extend(
            f"{index} - {meat['nome']}"
            for index, meat in enumerate(self.list_daily_meats(), start=1)
        )
        lines.extend(["", "Digite o número da marmita desejada."])
        return "\n".join(lines)

    def format_meat_menu(self, marmita_type: dict[str, Any]) -> str:
        count = int(marmita_type["quantidade_carnes"])
        label = "carne" if count == 1 else "carnes"
        lines = [
            f"Você escolheu {marmita_type['nome']}.",
            "",
            f"Escolha {count} {label}.",
        ]
        if count > 1:
            lines.append("Exemplo: 1 e 2")
        lines.append("")
        lines.extend(
            f"{index} - {meat['nome']}"
            for index, meat in enumerate(self.list_daily_meats(), start=1)
        )
        return "\n".join(lines)

    @staticmethod
    def _find_by_number_or_id(
        items: list[dict[str, Any]], value: str | int
    ) -> dict[str, Any] | None:
        text = str(value).strip()
        if text.isdigit():
            index = int(text) - 1
            return items[index] if 0 <= index < len(items) else None
        return next((item for item in items if item["id"] == text), None)


def format_currency(value: float) -> str:
    formatted = f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"
