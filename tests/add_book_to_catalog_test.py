import pytest
from library_service import (
    add_book_to_catalog
)
from database import (
    reset_test_additions,
)


def test_add_book_valid_input():
    """Test adding a book with valid input."""
    reset_test_additions()

    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    reset_test_additions()

    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_total_copies_negative():
    """Test adding a book with a negative number for total copies"""
    reset_test_additions()

    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890124", -1)

    assert success == False
    assert "positive integer" in message

def test_add_book_invalid_title_long():
    """Test adding a book with a title greater than 200 characters"""
    reset_test_additions()

    success, message = add_book_to_catalog("a" * 201, "Test Author", "1234567890124", 5)

    assert success == False
    assert "200 characters" in message

def test_add_book_invalid_author_long():
    """Test adding a book with an author greater than 100 characters"""
    reset_test_additions()

    success, message = add_book_to_catalog("Test Book", "a" * 101, "1234567890124", 5)

    assert success == False
    assert "100 characters" in message

def test_add_book_invalid_isbn_duplicate():
    """Test adding a book with the same ISBN as a previous book"""
    reset_test_additions()

    add_book_to_catalog("Test Book 1", "Test Author 1", "1234567890123", 5)
    success, message = add_book_to_catalog("Test Book 2", "Test Author 2", "1234567890123", 5)

    assert success == False
    assert "already exists" in message

def test_add_book_invalid_no_title():
    """Test adding a book with no title"""
    reset_test_additions()

    success, message = add_book_to_catalog("", "Test Author", "1234567890124", 5)

    assert success == False
    assert "Title is required" in message

def test_add_book_invalid_no_author():
    """Test adding a book with no author"""
    reset_test_additions()

    success, message = add_book_to_catalog("Test Book", "", "1234567890124", 5)

    assert success == False
    assert "Author is required" in message

def test_add_book_valid_edge_case():
    """Test the edge case of 200 character title and 100 character author"""
    reset_test_additions()

    success, message = add_book_to_catalog("a" * 200, "a" * 100, "1234567890124", 5)

    assert success == True
    assert "successfully added" in message