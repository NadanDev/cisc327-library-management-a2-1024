import pytest
from library_service import (
    get_patron_status_report,
    return_book_by_patron
)
from database import (
    reset_test_additions,
    insert_borrow_record
)
from datetime import datetime, timedelta


def test_patron_status_with_book():
    """Test patron status report with 1 borrowed book (no late fees)"""
    reset_test_additions()

    due_date = datetime.now() + timedelta(days=14)
    insert_borrow_record("123456", 1, datetime.now(), due_date)

    results = get_patron_status_report("123456")

    assert results["num_books_borrowed"] == 2 # Plus the already added one
    assert "gatsby" in results["books"][1]["title"].lower()
    assert results["books"][1]["due_date"] == due_date
    assert results["total_late_fees"] == 0.00


def test_patron_status_no_books():
    """Test patron status report with no borrowed books"""
    reset_test_additions()

    results = get_patron_status_report("654321")

    assert results["num_books_borrowed"] == 0
    assert results["books"] == []
    assert results["total_late_fees"] == 0.00


def test_patron_status_with_late_fees():
    """Test patron status report with an overdue book"""
    reset_test_additions()

    due_date = datetime.now() - timedelta(days=20)
    insert_borrow_record("654321", 3, datetime.now(), due_date)

    results = get_patron_status_report("654321")

    assert results["num_books_borrowed"] == 1
    assert "1984" in results["books"][0]["title"].lower()
    assert results["books"][0]["due_date"] == due_date
    assert results["total_late_fees"] == 15.00

def test_patron_status_with_mix():
    """Test patron status report with with a mix of books"""
    reset_test_additions()

    due_date1 = datetime.now() - timedelta(days=4)
    insert_borrow_record("567890", 2, datetime.now(), due_date1)

    due_date2 = datetime.now() + timedelta(days=14)
    insert_borrow_record("567890", 1, datetime.now(), due_date2)

    results = get_patron_status_report("567890")

    assert results["num_books_borrowed"] == 2
    assert ("gatsby" in results["books"][0]["title"].lower() or "gatsby" in results["books"][1]["title"].lower())
    assert ("mockingbird" in results["books"][0]["title"].lower() or "mockingbird" in results["books"][1]["title"].lower())
    assert (results["books"][0]["due_date"] == due_date1 or results["books"][1]["due_date"] == due_date1)
    assert (results["books"][0]["due_date"] == due_date2 or results["books"][1]["due_date"] == due_date2)
    assert results["total_late_fees"] == 2.00


def test_patron_status_invalid_id():
    """Test patron status report with invalid patron ID."""
    reset_test_additions()

    results = get_patron_status_report("123")

    assert results == {}

def test_patron_status_history():
    """Test patron status report with a previously borrowed book"""
    reset_test_additions()

    return_book_by_patron("123456", 3)
    results = get_patron_status_report("123456")

    assert results["borrowing_history"][0]["title"] == "1984"



if (__name__ == "__main__"):
    test_patron_status_with_book()
    test_patron_status_no_books()
    test_patron_status_with_late_fees()
    test_patron_status_with_mix()
    test_patron_status_invalid_id()
    test_patron_status_history()