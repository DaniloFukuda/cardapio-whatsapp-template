def test_add_item_and_calculate_totals(menu_service, order_service):
    cart = order_service.empty_cart()
    product = menu_service.get_product("marmita-media")

    cart = order_service.add_item(cart, product, 2)
    cart = order_service.add_item(cart, product, 1)
    totals = order_service.calculate_totals(cart["items"], "entrega")

    assert cart["items"][0]["quantity"] == 3
    assert totals == {"subtotal": 66.0, "delivery_fee": 5.0, "total": 71.0}


def test_create_order_and_format_staff_message(order_service):
    session = {
        "customer_phone": "5561999999999",
        "customer_name": "João",
        "delivery_type": "entrega",
        "address": "Rua X, 123",
        "payment_method": "pix",
        "notes": "Sem cebola.",
        "cart": {
            "items": [
                {
                    "product_id": "marmita-media",
                    "name": "Marmita Média",
                    "unit_price": 22.0,
                    "quantity": 2,
                }
            ],
            "context": {},
        },
    }

    order = order_service.create_order(session)
    message = order_service.format_staff_message(order)

    assert order["order_number"] == "PED-000001"
    assert order["total"] == 49.0
    assert "🔔 NOVO PEDIDO - PED-000001" in message
    assert "- 2x Marmita Média - R$ 44,00" in message
    assert "Sem cebola." in message
