from services.session_service import (
    AFTER_ADD,
    AWAITING_DELIVERY_TYPE,
    AWAITING_MARMITA,
    AWAITING_MEATS,
)


def test_basic_marmita_session_transitions(session_service):
    phone = "5561999999999"

    greeting = session_service.handle_message(phone, "cardápio")
    menu = session_service.handle_message(phone, "1")
    session = session_service.get_or_create_session(phone)

    assert "Bem-vindo" in greeting.reply
    assert "Cardápio de hoje" in menu.reply
    assert session["current_state"] == AWAITING_MARMITA

    meat_menu = session_service.handle_message(phone, "2")
    session = session_service.get_or_create_session(phone)
    assert "Escolha 2 carnes" in meat_menu.reply
    assert session["current_state"] == AWAITING_MEATS

    session_service.handle_message(phone, "1,2")
    result = session_service.handle_message(phone, "2")
    session = session_service.get_or_create_session(phone)

    assert "2x Marmita com 2 carnes" in result.reply
    assert "Carnes: Churrasco e Frango" in result.reply
    assert session["current_state"] == AFTER_ADD
    assert session["cart"]["items"][0]["quantity"] == 2


def test_repeated_meat_keeps_selection_state(session_service):
    phone = "5561888888888"
    for message in ["oi", "1", "2"]:
        session_service.handle_message(phone, message)

    result = session_service.handle_message(phone, "1 e 1")
    session = session_service.get_or_create_session(phone)

    assert "Não repita a mesma carne" in result.reply
    assert session["current_state"] == AWAITING_MEATS


def test_checkout_reaches_customer_data(session_service):
    phone = "5561777777777"
    for message in ["oi", "1", "1", "1", "1", "3", "Maria"]:
        result = session_service.handle_message(phone, message)

    session = session_service.get_or_create_session(phone)
    assert session["current_state"] == AWAITING_DELIVERY_TYPE
    assert "1 - Entrega" in result.reply


def test_cancel_clears_cart(session_service):
    phone = "5561666666666"
    for message in ["oi", "1", "1", "1", "2", "0"]:
        result = session_service.handle_message(phone, message)

    session = session_service.get_or_create_session(phone)
    assert "Pedido cancelado" in result.reply
    assert session["cart"]["items"] == []
