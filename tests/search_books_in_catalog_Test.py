import pytest
from library_service import (
    search_books_in_catalog
)
from database import (
    reset_test_additions,
)


def test_search_books_title_partial():
    """Test searching for The Great Gatsby with partial title search"""
    results = search_books_in_catalog("gatsby", "title")

    for book in results: # Every book in result should have gatsby in the title
        assert("gatsby" in book["title"].lower())


def test_search_books_by_author_partial():
    """Test searching for To Kill A Mockingbird with partial author search"""
    results = search_books_in_catalog("lee", "author")

    for book in results: # Every book in result should have lee in the author
        assert("lee" in book["author"].lower())


def test_search_books_by_isbn_exact():
    """Test searching for 1984 with exact ISBN search"""
    results = search_books_in_catalog("9780451524935", "isbn")

    assert results[0]["title"] == "1984" # Should only be 1 result which is 1984


def test_search_books_no_results():
    """Test searching for nothing using random search"""
    results = search_books_in_catalog("abcdefghijk", "title")

    assert results == []

def test_search_books_wrong_isbn():
    """Test searching with ISBN that is not exactly 13 digits"""
    results = search_books_in_catalog("123", "isbn")

    assert results == []



if (__name__ == "__main__"):
    reset_test_additions() # Function to reset the book and borrow records added by these tests

    test_search_books_title_partial()
    test_search_books_by_author_partial()
    test_search_books_by_isbn_exact()
    test_search_books_no_results()
    test_search_books_wrong_isbn()