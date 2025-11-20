from flask import url_for
from playwright.sync_api import Page, expect
from database import (
    reset_test_additions,
)

def test_add_and_borrow_book(page: Page):
    """Ensure end to end functions properly for adding and borrowing the book"""
    reset_test_additions()

    page.goto("http://localhost:5000")
    expect(page).to_have_url("http://localhost:5000/catalog") # Should start on catalog

    # Go to Add Book page
    page.get_by_role("link", name="➕ Add New Book").click()
    expect(page).to_have_url("http://localhost:5000/add_book")

    # Fill inputs and verify the book is in catalog
    page.get_by_role("textbox", name="Title *").click()
    page.get_by_role("textbox", name="Title *").fill("My Book")
    page.get_by_role("textbox", name="Author *").click()
    page.get_by_role("textbox", name="Author *").fill("Me")
    page.get_by_role("textbox", name="ISBN *").click()
    page.get_by_role("textbox", name="ISBN *").fill("1234567891011")
    page.get_by_role("spinbutton", name="Total Copies *").click()
    page.get_by_role("spinbutton", name="Total Copies *").fill("5")
    page.get_by_role("button", name="Add Book to Catalog").click()
    expect(page.get_by_text("Book \"My Book\" has been successfully added to the catalog.")).to_be_visible()
    expect(page.get_by_text("1234567891011")).to_be_visible()

    # Borrow the book
    page.get_by_role("row", name="4 My Book Me 1234567891011 5/").get_by_placeholder("Patron ID (6 digits)").click()
    page.get_by_role("row", name="4 My Book Me 1234567891011 5/").get_by_placeholder("Patron ID (6 digits)").fill("123456")
    page.get_by_role("cell", name="123456 Borrow").get_by_role("button").click()
    expect(page.get_by_text("Successfully borrowed \"My Book\". Due date:")).to_be_visible()

def test_search_borrow_return_book(page: Page):
    """Ensure end to end functions properly for searching, borrowing, and returning the book"""
    reset_test_additions()

    page.goto("http://localhost:5000")
    expect(page).to_have_url("http://localhost:5000/catalog")

    # Go to Search page
    page.get_by_role("link", name="🔍 Search").click()
    expect(page).to_have_url("http://localhost:5000/search")

    # Fill in search and verify the correct book appears
    page.get_by_role("textbox", name="Search Term").click()
    page.get_by_role("textbox", name="Search Term").fill("The Great")
    page.get_by_role("button", name="🔍 Search").click()
    expect(page.get_by_text("Search Results for \"The Great\"")).to_be_visible()
    expect(page.get_by_text("9780743273565")).to_be_visible()

    # Borrow the book
    page.get_by_role("textbox", name="Patron ID").click()
    page.get_by_role("textbox", name="Patron ID").fill("123456")
    page.get_by_role("button", name="Borrow").click()
    expect(page.get_by_text("Successfully borrowed \"The Great Gatsby\". Due date:")).to_be_visible()

    # Go to Return Book page
    page.get_by_role("link", name="↩️ Return Book").click()
    expect(page).to_have_url("http://localhost:5000/return")

    # Fill in return form and verify success message
    page.get_by_role("textbox", name="Patron ID *").click()
    page.get_by_role("textbox", name="Patron ID *").fill("123456")
    page.get_by_role("spinbutton", name="Book ID *").click()
    page.get_by_role("spinbutton", name="Book ID *").fill("1")
    page.get_by_role("button", name="Process Return").click()
    expect(page.get_by_text("Successfully returned \"The Great Gatsby\"")).to_be_visible()

def test_borrow_check_status(page: Page):
    """Ensure end to end functions properly for borrowing and checking patron status for the book"""
    reset_test_additions()

    page.goto("http://localhost:5000")
    expect(page).to_have_url("http://localhost:5000/catalog")

    # Borrow the book
    page.get_by_role("row", name="2 To Kill a Mockingbird").get_by_placeholder("Patron ID (6 digits)").click()
    page.get_by_role("row", name="2 To Kill a Mockingbird").get_by_placeholder("Patron ID (6 digits)").fill("123456")
    page.get_by_role("cell", name="123456 Borrow").get_by_role("button").click()
    expect(page.get_by_text("Successfully borrowed \"To Kill a Mockingbird\". Due date:")).to_be_visible()

    # Go to Patron Status page
    page.get_by_role("link", name="📋 Patron Status").click()
    expect(page).to_have_url("http://localhost:5000/status")

    # Fill in patron ID and make sure borrowed book appears
    page.get_by_role("textbox", name="Patron ID *").click()
    page.get_by_role("textbox", name="Patron ID *").fill("123456")
    page.get_by_role("button", name="Check Status").click()
    expect(page.get_by_text("Status for Patron ID: 123456")).to_be_visible()
    expect(page.get_by_text("To Kill a Mockingbird")).to_be_visible()