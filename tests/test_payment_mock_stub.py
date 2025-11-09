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
    """Test a valid payment by mocking success of the process_payment function and entering correct values"""
    # Stubs: returns values for separate functions
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 10.0})
    mocker.patch("services.library_service.get_book_by_id", return_value = {"title": "The Great Gatsby"}) # Simply do title for simplicity

    # Mocks: return values for PaymentGateway functions
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway) # Call the function

    assert success is True
    assert "Payment successful!" in msg
    assert txn == "txn_123"

    # Has to be called once with these arguments
    mock_gateway.process_payment.assert_called_once()
    mock_gateway.process_payment.assert_called_with(patron_id = "123456", amount = 10.0, description = "Late fees for 'The Great Gatsby'")

def test_pay_late_fees_declined(mocker):
    """Test an invalid payment by mocking failure of the process_payment function"""
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 10.0})
    mocker.patch("services.library_service.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Declined By Gateway")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "Declined By Gateway" in msg
    assert txn is None

    mock_gateway.process_payment.assert_called_once()
    mock_gateway.process_payment.assert_called_with(patron_id = "123456", amount = 10.0, description = "Late fees for 'The Great Gatsby'")

def test_pay_late_fees_invalid_patronid(mocker):
    """Test pay_late_fees with an invalid patron id (failure)"""
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 10.0})
    mocker.patch("services.library_service.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    # Shouldn't need this line but keep it in case pay_late_fees didn't fail as expected (same with other functions)
    mock_gateway.process_payment.return_value = (False, "", "Shouldn't Reach")
    success, msg, txn = pay_late_fees("12345", 1, mock_gateway)

    assert success is False
    assert "Invalid patron ID." in msg
    assert txn is None

    # Should fail before calling process_payment
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_zero_late_fee(mocker):
    """Test pay_late_fees failure by stubbing the late fee calculation to 0"""
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 0.0})
    mocker.patch("services.library_service.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Shouldn't Reach")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "No late fees" in msg
    assert txn is None

    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_network_error(mocker):
    """Test a network error by mocking an error on process_payment"""
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 10.0})
    mocker.patch("services.library_service.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = Exception("Bad Network")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "Payment processing error" in msg
    assert txn is None

    mock_gateway.process_payment.assert_called_once()
    mock_gateway.process_payment.assert_called_with(patron_id = "123456", amount = 10.0, description = "Late fees for 'The Great Gatsby'")

# Additional Tests to complete statement coverage:
def test_pay_late_fees_invalid_fee_info(mocker):
    """Test pay_late_fees failure where calculate_late_fee_for_book fails"""
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_not_amount": 10.0})
    mocker.patch("services.library_service.get_book_by_id", return_value = {"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Shouldn't Reach")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "Unable to calculate" in msg
    assert txn is None

    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_invalid_no_book(mocker):
    """Test pay_late_fees failure where the payment gateway is None"""
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value = {"fee_amount": 10.0})
    mocker.patch("services.library_service.get_book_by_id", return_value = None)

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Shouldn't Reach")
    success, msg, txn = pay_late_fees("123456", 1, None)

    assert success is False
    assert "Book not found" in msg
    assert txn is None

    mock_gateway.process_payment.assert_not_called()



def test_refund_late_fee_valid():
    """Test a valid refund by mocking a success of refund_payment"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund of $10.0 processed successfully.")
    success, msg = refund_late_fee_payment("txn_123", 10.0, mock_gateway)

    assert success is True
    assert "$10.0 processed successfully" in msg

    # Must be called once with these arguments
    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_with("txn_123", 10.0)

def test_refund_late_fee_invalid_transactionid():
    """Test an invalid refund by passing an invalid transaction ID"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "", "Shouldn't Reach")
    success, msg = refund_late_fee_payment("tx_123", 10.0, mock_gateway)

    assert success is False
    assert "Invalid transaction ID." in msg

    # Should fail before calling refund_payment
    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_zero_amount():
    """Test an invalid refund by passing $0 refund"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "", "Shouldn't Reach")
    success, msg = refund_late_fee_payment("txn_123", 0, mock_gateway)

    assert success is False
    assert "greater than 0" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_negative_amount():
    """Test an invalid refund by passing negative refund"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "", "Shouldn't Reach")
    success, msg = refund_late_fee_payment("txn_123", -1, mock_gateway)

    assert success is False
    assert "greater than 0" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_exceed_max_amount():
    """Test an invalid refund by passing refund beyond the max of 15"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "", "Shouldn't Reach")
    success, msg = refund_late_fee_payment("txn_123", 16, mock_gateway)

    assert success is False
    assert "maximum late fee" in msg

    mock_gateway.refund_payment.assert_not_called()

    # Additional tests to complete statement coverage
def test_refund_late_fee_error():
    """Test an error by mocking an error on refund_payment"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = Exception("Error")
    success, msg = refund_late_fee_payment("txn_123", 10.0, mock_gateway)

    assert success is False
    assert "Refund processing error" in msg

    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_with("txn_123", 10.0)

def test_refund_late_fee_declined():
    """Test an invalid refund by mocking failure of the refund_payment function"""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Declined By Gateway")
    success, msg = refund_late_fee_payment("txn_123", 10.0, mock_gateway)

    assert success is False
    assert "Declined By Gateway" in msg

    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_with("txn_123", 10.0)