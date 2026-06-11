from services.session_service import (
    AFTER_ADD,
    AWAITING_CATEGORY,
    AWAITING_DELIVERY_TYPE,
    AWAITING_PRODUCT,
)


def test_basic_session_transitions(session_service):
    phone = "5561999999999"

    greeting = session_service.handle_message(phone, "cardápio")
    categories = session_service.handle_message(phone, "1")
    session = session_service.get_or_create_session(phone)

    assert "Bem-vindo" in greeting.reply
    assert "Cardápio:" in categories.reply
    assert session["current_state"] == AWAITING_CATEGORY

    session_service.handle_message(phone, "1")
    session = session_service.get_or_create_session(phone)
    assert session["current_state"] == AWAITING_PRODUCT

    session_service.handle_message(phone, "2")
    result = session_service.handle_message(phone, "2")
    session = session_service.get_or_create_session(phone)

    assert "2x Marmita Média" in result.reply
    assert session["current_state"] == AFTER_ADD
    assert session["cart"]["items"][0]["quantity"] == 2


def test_checkout_reaches_customer_data(session_service):
    phone = "5561888888888"
    for message in ["oi", "1", "1", "1", "1", "3", "Maria"]:
        result = session_service.handle_message(phone, message)

    session = session_service.get_or_create_session(phone)
    assert session["current_state"] == AWAITING_DELIVERY_TYPE
    assert "1 - Entrega" in result.reply


def test_cancel_clears_cart(session_service):
    phone = "5561777777777"
    for message in ["oi", "1", "1", "1", "2", "0"]:
        result = session_service.handle_message(phone, message)

    session = session_service.get_or_create_session(phone)
    assert "Pedido cancelado" in result.reply
    assert session["cart"]["items"] == []
