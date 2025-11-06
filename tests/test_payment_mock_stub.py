import pytest
from unittest.mock import Mock
from services.library_service import (
    pay_late_fees,
    refund_late_fee_payment
)
from services.payment_service import (
    PaymentGateway
)

def test_pay_late_fees_valid(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 10.0})
    mocker.patch("database.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is True
    assert "Payment successful!" in msg
    assert txn == "txn_123"

    mock_gateway.process_payment.assert_called_once_with(patron_id = "123456", amount = 10.0, description = "Late fees for 'The Great Gatsby'")

def test_pay_late_fees_declined(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 10.0})
    mocker.patch("database.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Declined By Gateway")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "Declined By Gateway" in msg
    assert txn is None

    mock_gateway.process_payment.assert_called_once_with(patron_id = "123456", amount = 10.0, description = "Late fees for 'The Great Gatsby'")

def test_pay_late_fees_invalid_patronid(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 10.0})
    mocker.patch("database.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    success, msg, txn = pay_late_fees("12345", 1, mock_gateway)

    assert success is False
    assert "Invalid patron ID." in msg
    assert txn is None

    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_zero_late_fee(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 0.0})
    mocker.patch("database.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "No late fees" in msg
    assert txn is None

    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_network_error(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 10.0})
    mocker.patch("database.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = Exception("Bad Network")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "Payment processing error" in msg
    assert txn is None

    mock_gateway.process_payment.assert_called_once_with(patron_id = "123456", amount = 10.0, description = "Late fees for 'The Great Gatsby'")


def test_refund_late_fee_valid(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund of $10.0 processed successfully.")
    success, msg = refund_late_fee_payment("txn_123", 10.0, mock_gateway)

    assert success is True
    assert "$10.0 processed successfully" in msg

    mock_gateway.refund_payment.assert_called_once_with("txn_123", 10.0)

def test_refund_late_fee_invalid_transactionid(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("tx_123", 10.0, mock_gateway)

    assert success is False
    assert "Invalid transaction ID." in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_zero_amount(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("txn_123", 0, mock_gateway)

    assert success is False
    assert "greater than 0" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_negative_amount(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("txn_123", -1, mock_gateway)

    assert success is False
    assert "greater than 0" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_exceed_max_amount(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("txn_123", 16, mock_gateway)

    assert success is False
    assert "maximum late fee" in msg

    mock_gateway.refund_payment.assert_not_called()