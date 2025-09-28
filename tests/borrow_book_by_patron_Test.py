import pytest
from library_service import (
    add_book_to_catalog,
    borrow_book_by_patron
)
from database import (
    get_patron_borrow_count,
    reset_test_additions,
    get_book_by_id
)


def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""
    success, message = borrow_book_by_patron("123456", 1)
    
    assert(get_book_by_id(1)["available_copies"] == 2) # Updates available copies properly (starts with 3 and 1 borrowed)
    assert get_patron_borrow_count("123456") == 2 # Creates borrowing record properly (starts at 1)
    assert success == True
    assert "Successfully borrowed" in message

    reset_test_additions()

def test_borrow_book_invalid_patronid():
    """Test borrowing a book with invalid patron ID"""
    success, message = borrow_book_by_patron("12345", 1)

    assert success == False
    assert "6 digits" in message

    reset_test_additions()

def test_borrow_book_invalid_not_found():
    """Test borrowing a book that does not exist"""
    success, message = borrow_book_by_patron("123456", 4) # Book ID 4 does not exist

    assert success == False
    assert "not found" in message

    reset_test_additions()

def test_borrow_book_invalid_not_available():
    """Test borrowing a book with 0 available copies"""
    success, message = borrow_book_by_patron("123456", 3) # Book ID 3 has no copies available

    assert success == False
    assert "not available" in message

    reset_test_additions()

def test_borrow_book_invalid_too_many():
    """Test borrowing a book with 5 books already borrowed"""

    # Fill borrow record
    borrow_book_by_patron("123456", 1)
    borrow_book_by_patron("123456", 1)
    borrow_book_by_patron("123456", 1)
    borrow_book_by_patron("123456", 2)
    borrow_book_by_patron("123456", 2)

    assert get_patron_borrow_count("123456") == 6 # 1 already added so 5 + 1 = 6

    # Add new book to borrow
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 1)

    # Borrow newly added book
    success, message = borrow_book_by_patron("123456", 4)

    assert success == False
    assert "maximum borrowing" in message

    reset_test_additions()



if (__name__ == "__main__"):
    reset_test_additions() # Function to reset the borrow records added by these tests

    test_borrow_book_valid_input()
    test_borrow_book_invalid_patronid()
    test_borrow_book_invalid_not_found
    test_borrow_book_invalid_not_available()
    test_borrow_book_invalid_too_many()