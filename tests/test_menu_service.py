import pytest


def test_marmita_prices(menu_service):
    small = menu_service.get_marmita_type("marmita-pequena-1-carne")
    two_meats = menu_service.get_marmita_type(2)

    assert small["preco"] == 21.0
    assert small["quantidade_carnes"] == 1
    assert two_meats["id"] == "marmita-2-carnes"
    assert two_meats["preco"] == 23.0


def test_list_meats_and_fixed_barbecue(menu_service):
    meats = menu_service.list_daily_meats()

    assert [meat["nome"] for meat in meats] == [
        "Churrasco",
        "Frango",
        "Carne de panela",
    ]
    assert menu_service.get_meat("churrasco")["fixo"] is True
    assert menu_service.get_meat(2)["id"] == "frango"


@pytest.mark.parametrize("value", ["1 e 2", "1,2", "1 2", "1/2"])
def test_parse_two_meats_in_supported_formats(menu_service, value):
    meats = menu_service.parse_meat_choices(value)

    assert [meat["id"] for meat in meats] == ["churrasco", "frango"]


def test_validate_one_and_two_meats(menu_service):
    small = menu_service.get_marmita_type(1)
    two_meats = menu_service.get_marmita_type(2)
    barbecue = menu_service.parse_meat_choices("1")
    pair = menu_service.parse_meat_choices("1 e 2")

    menu_service.validate_meat_choices(small, barbecue)
    menu_service.validate_meat_choices(two_meats, pair)

    with pytest.raises(ValueError, match="exatamente 1 carne"):
        menu_service.validate_meat_choices(small, pair)
    with pytest.raises(ValueError, match="exatamente 2 carnes"):
        menu_service.validate_meat_choices(two_meats, barbecue)


def test_reject_repeated_meat(menu_service):
    with pytest.raises(ValueError, match="Não repita"):
        menu_service.parse_meat_choices("1 e 1")


def test_parse_meats_by_id(menu_service):
    meats = menu_service.parse_meat_choices("churrasco/carne-de-panela")

    assert [meat["id"] for meat in meats] == ["churrasco", "carne-de-panela"]


def test_format_daily_menu(menu_service):
    text = menu_service.format_daily_menu()

    assert "Cardápio de hoje 🍽️" in text
    assert "Marmita pequena - 1 carne - R$ 21,00" in text
    assert "Marmita com 2 carnes - R$ 23,00" in text
    assert "1 - Churrasco" in text
