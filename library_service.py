"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, 
    get_patron_borrowed_books, get_patron_borrow_history
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars) 
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to return a book.
    Implements R4 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to return
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits"
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found"
    
    # Verifies the book was borrowed by the patron
    if not any(book["id"] == b["book_id"] for b in get_patron_borrowed_books(patron_id)):
        return False, "Cannot return book that was not borrowed"
    
    # Calculate late fee before submitting record
    late_fees = calculate_late_fee_for_book(patron_id, book_id)["fee_amount"]

    # Create return record and insert it
    return_date = datetime.now()
    return_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not return_success:
        return False, "Database error occurred while updating borrow record"
    
    # Update availability
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occured while updating book availability"
    
    return True, f'Successfully returned "{book["title"]}" on {return_date.strftime("%Y-%m-%d")}. Late fees: ${late_fees}.'

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Returns JSON response with fee amount and days overdue.
    Implements R5 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to calculate fees for
        
    Returns:
        Dict: {'fee_amount': double, 'days_overdue': int}
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {"fee_amount": 0, "days_overdue": 0}
    
    # Check if book has been borrowed
    all_books = get_patron_borrowed_books(patron_id)
    book = None
    for b in all_books:
        if (book_id == b["book_id"]):
            book = b
            break

    if book == None:
        return {"fee_amount": 0, "days_overdue": 0}
    
    # Calculate days overdue
    due_date = book["due_date"]
    date = datetime.now()
    days_overdue = (date - due_date).days

    if (days_overdue < 1):
        return {"fee_amount": 0, "days_overdue": 0}

    # Calculate fees based on days overdue (max 15)
    fee_amount = 0
    if (days_overdue <= 7):
        fee_amount = 0.50 * days_overdue
    else:
        fee_amount = 3.50 + (days_overdue - 7)
    
    if (fee_amount > 15.00):
        fee_amount = 15.00

    return {"fee_amount": fee_amount, "days_overdue": days_overdue}

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Allows patron to search for a book given search term and type.
    Implements R6 as per requirements
    
    Args:
        search_term: String to search title/author/ISBN
        search_type: Type of title/author/ISBN
        
    Returns:
        List[Dict]: [{book1}, {book2}]
    """
    
    search_results = []
    all_books = get_all_books()
    if (search_type == "isbn"): # Search exact ISBN
        for book in all_books:
            if search_term == book["isbn"]:
                search_results.append(book)
    else: # Search partial title or author
        for book in all_books:
            if search_term.lower() in (book["title"].lower() if search_type == "title" else book["author"].lower()):
                search_results.append(book)

    return search_results

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Allows patron to search their status
    Implements R7 as per requirements
    
    Args:
        patron_id: 6-digit library card ID
        
    Returns:
        Dict: {'books': List{Dict}, 'total_late_fees': double, 'num_books_borrowed': int, 'borrowing_history': List[Dict]}
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {}
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    num_books_borrowed = len(borrowed_books)
    borrowing_history = get_patron_borrow_history(patron_id)
    total_late_fees = 0
    for book in borrowed_books:
        total_late_fees += calculate_late_fee_for_book(patron_id, book["book_id"])["fee_amount"]

    return {"books": borrowed_books, "total_late_fees": total_late_fees, "num_books_borrowed": num_books_borrowed, "borrowing_history": borrowing_history}
