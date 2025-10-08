import pytest
from library_service import (
    return_book_by_patron,
    borrow_book_by_patron
)
from database import (
    get_patron_borrow_count,
    get_book_by_id,
    reset_test_additions
)


def test_return_book_valid():
    """Test returning a book with valid input."""
    reset_test_additions()

    borrow_book_by_patron("123456", 1) # Borrow a book to return
    success, message = return_book_by_patron("123456", 1)
    
    assert(get_book_by_id(1)["available_copies"] == 3) # All available copies should be available
    assert get_patron_borrow_count("123456") == 1 # Patron should have no books borrowed
    assert success == True
    assert "Successfully returned" in message

def test_return_book_invalid_patronid():
    """Test returning a book with invalid patron ID"""
    reset_test_additions()

    success, message = return_book_by_patron("12345", 1)

    assert success == False
    assert "6 digits" in message

def test_return_book_invalid_not_borrowed():
    """Test returning a book that was not borrowed"""
    reset_test_additions()

    success, message = return_book_by_patron("123456", 2)

    assert success == False
    assert "not borrowed" in message

def test_return_book_invalid_wrong_patron():
    """Test returning a book that another patron borrowed"""
    reset_test_additions()

    borrow_book_by_patron("123456", 1)
    success, message = return_book_by_patron("654321", 1)

    assert success == False
    assert "not borrowed" in message

def test_return_book_invalid_ID():
    """Test returning a book that doesn't exist"""
    reset_test_additions()

    success, message = return_book_by_patron("123456", 99)

    assert success == False
    assert "not found" in message