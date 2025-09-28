import pytest
from library_service import (
    add_book_to_catalog
)
from database import (
    reset_test_additions,
)


def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message

    reset_test_additions()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

    reset_test_additions()

def test_add_book_invalid_total_copies_negative():
    """Test adding a book with a negative number for total copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890124", -1)

    assert success == False
    assert "positive integer" in message

    reset_test_additions()

def test_add_book_invalid_title_long():
    """Test adding a book with a title greater than 200 characters"""
    success, message = add_book_to_catalog("a" * 201, "Test Author", "1234567890124", 5)

    assert success == False
    assert "200 characters" in message

    reset_test_additions()

def test_add_book_invalid_author_long():
    """Test adding a book with an author greater than 100 characters"""
    success, message = add_book_to_catalog("Test Book", "a" * 101, "1234567890124", 5)

    assert success == False
    assert "100 characters" in message

    reset_test_additions()

def test_add_book_invalid_isbn_duplicate():
    """Test adding a book with the same ISBN as a previous book"""
    add_book_to_catalog("Test Book 1", "Test Author 1", "1234567890123", 5)
    success, message = add_book_to_catalog("Test Book 2", "Test Author 2", "1234567890123", 5)

    assert success == False
    assert "already exists" in message

    reset_test_additions()

def test_add_book_invalid_no_title():
    """Test adding a book with no title"""
    success, message = add_book_to_catalog("", "Test Author", "1234567890124", 5)

    assert success == False
    assert "Title is required" in message

    reset_test_additions()

def test_add_book_invalid_no_author():
    """Test adding a book with no author"""
    success, message = add_book_to_catalog("Test Book", "", "1234567890124", 5)

    assert success == False
    assert "Author is required" in message

    reset_test_additions()

def test_add_book_valid_edge_case():
    """Test the edge case of 200 character title and 100 character author"""
    success, message = add_book_to_catalog("a" * 200, "a" * 100, "1234567890124", 5)

    assert success == True
    assert "successfully added" in message

    reset_test_additions()



if (__name__ == "__main__"):
    reset_test_additions() # Function to reset the books added by these tests

    test_add_book_valid_input()
    test_add_book_invalid_isbn_too_short()
    test_add_book_invalid_total_copies_negative()
    test_add_book_invalid_title_long()
    test_add_book_invalid_author_long()
    test_add_book_invalid_isbn_duplicate()
    test_add_book_invalid_no_title()
    test_add_book_invalid_no_author()
    test_add_book_valid_edge_case()