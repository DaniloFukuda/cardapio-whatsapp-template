def test_list_categories(menu_service):
    categories = menu_service.list_categories()

    assert [category["id"] for category in categories] == [
        "marmitas",
        "pratos-feitos",
        "bebidas",
        "adicionais",
    ]


def test_find_product(menu_service):
    product = menu_service.get_product("marmita-media")

    assert product is not None
    assert product["nome"] == "Marmita Média"
    assert product["preco"] == 22.0
    assert product["categoria_id"] == "marmitas"


def test_format_menu(menu_service):
    text = menu_service.format_products_menu("bebidas")

    assert "Bebidas:" in text
    assert "Refrigerante Lata - R$ 3,50" in text
