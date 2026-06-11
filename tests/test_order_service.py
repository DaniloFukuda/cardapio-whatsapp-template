def build_item(menu_service, order_service, marmita_number, meat_input, quantity):
    marmita = menu_service.get_marmita_type(marmita_number)
    meats = menu_service.parse_meat_choices(meat_input)
    menu_service.validate_meat_choices(marmita, meats)
    return order_service.add_item(
        order_service.empty_cart(), marmita, meats, quantity
    )


def test_add_item_calculates_quantity_and_total(menu_service, order_service):
    cart = build_item(menu_service, order_service, 2, "1 e 2", 2)
    totals = order_service.calculate_totals(cart["items"], "retirada")

    assert cart["items"][0]["unit_price"] == 23.0
    assert cart["items"][0]["quantity"] == 2
    assert totals == {"subtotal": 46.0, "delivery_fee": 0.0, "total": 46.0}


def test_format_cart_item(menu_service, order_service):
    cart = build_item(menu_service, order_service, 2, "1/2", 2)
    text = order_service.format_item(cart["items"][0])

    assert text == (
        "2x Marmita com 2 carnes\n"
        "Carnes: Churrasco e Frango\n"
        "Valor unitário: R$ 23,00\n"
        "Total: R$ 46,00"
    )


def test_create_order_and_format_staff_message(menu_service, order_service):
    cart = build_item(menu_service, order_service, 2, "1 e 2", 2)
    session = {
        "customer_phone": "5561999999999",
        "customer_name": "João",
        "delivery_type": "retirada",
        "address": None,
        "payment_method": "pix",
        "notes": None,
        "cart": cart,
    }

    order = order_service.create_order(session)
    message = order_service.format_staff_message(order)

    assert order["order_number"] == "PED-000001"
    assert order["total"] == 46.0
    assert "- 2x Marmita com 2 carnes" in message
    assert "Carnes: Churrasco e Frango" in message
    assert "Unitário: R$ 23,00" in message
    assert "Total: R$ 46,00" in message
