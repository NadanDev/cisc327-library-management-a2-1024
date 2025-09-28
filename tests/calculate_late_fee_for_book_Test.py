import pytest
from library_service import (
    calculate_late_fee_for_book
)
from database import (
    reset_test_additions,
    insert_borrow_record
)
from datetime import datetime, timedelta


def test_late_fee_no_overdue():
    """Test late fee when book is returned on time"""
    due_date = datetime.now() + timedelta(days=14)
    insert_borrow_record("123456", 1, datetime.now(), due_date)
    result = calculate_late_fee_for_book("123456", 1)

    assert result["days_overdue"] == 0
    assert result["fee_amount"] == 0.00

    reset_test_additions() # Required since I'm using book ID 1 for all tests

def test_late_fee_4_days_overdue():
    """Test late fee for 4 days overdue"""
    due_date = datetime.now() - timedelta(days=4)
    insert_borrow_record("123456", 1, datetime.now(), due_date)
    result = calculate_late_fee_for_book("123456", 1)

    assert result["days_overdue"] == 4
    assert result["fee_amount"] == 2.00

    reset_test_additions()

def test_late_fee_10_days_overdue():
    """Test late fee for 10 days overdue"""
    due_date = datetime.now() - timedelta(days=10)
    insert_borrow_record("123456", 1, datetime.now(), due_date)
    result = calculate_late_fee_for_book("123456", 1)

    assert result["days_overdue"] == 10
    assert result["fee_amount"] == 6.50

    reset_test_additions()

def test_late_fee_20_days_overdue():
    """Test late fee for 20 days overdue (cap)"""
    due_date = datetime.now() - timedelta(days=20)
    insert_borrow_record("123456", 1, datetime.now(), due_date)
    result = calculate_late_fee_for_book("123456", 1)

    assert result["days_overdue"] == 20
    assert result["fee_amount"] == 15.00

    reset_test_additions()

def test_late_fee_invalid_patronid():
    """Test late fee for invalid patron ID"""
    result = calculate_late_fee_for_book("abc", 1)

    assert result["days_overdue"] == 0
    assert result["fee_amount"] == 0.00

    reset_test_additions()

def test_late_fee_book_not_borrowed():
    """Test late fee for book that was not borrowed"""
    result = calculate_late_fee_for_book("123456", 99)

    assert result["days_overdue"] == 0
    assert result["fee_amount"] == 0.00

    reset_test_additions()



if (__name__ == "__main__"):
    reset_test_additions() # Function to reset the book and borrow records added by these tests

    test_late_fee_no_overdue()
    test_late_fee_4_days_overdue()
    test_late_fee_10_days_overdue()
    test_late_fee_20_days_overdue()
    test_late_fee_invalid_patronid()
    test_late_fee_book_not_borrowed()