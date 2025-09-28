### Nathan Daneliak - 20391024




| Function Name | Implementation Status | What Is Missing (according to requirements_specification.md) |
|---------------|-----------------------|-----------------|
| R1: add_book_to_catalog | Complete | Nothing missing |
| R2: Book Catalog Display | Complete | Nothing missing |
| R3: borrow_book_by_patron | Complete | Nothing missing |
| R4: return_book_by_patron | Partial | Working GUI and properly accepts book ID and patron ID as perameters but lacks remaining R4 requirements: Verifies the book was borrowed by the patron, updates available copies and records return date, calculates and displays any late fees owed.|
| R5: calculate_late_fee_for_book | Incomplete | R5 requirements not implemented: Does not verify book is late (14 days after borrowing), does not calculate required fee, does not cap fee at $15.00, and does not return JSON response with fee amount and days overdue. |
| R6: search_books_in_catalog | Partial | Search page with search term and type created but lacks remaining R6 requirements: Does not support partial matching for title/author or exact matching for ISBN. Does not return results in the same format as the catalog. |
| R7: get_patron_status_report | Incomplete | Patron status page not created and R7 requirements not implemented: Cannot view currently borrowed books with due dates, total late fees owed, number of books currently borrowed, or borrowing history. |
<br><br>

Test scripts have been added in the "tests" folder. Each script contains test functions for each function contained in library_service.py. I've added a new function to database.py to reset the database when the test functions are run. This makes sure that the test functions work properly and don't fill the database with test information. R1 and R3 are tested according to the implemented code and the specification while R4-R7 are tested according to only the specification and thus have assumed some information. The test scripts must be run outside of the tests folder to import functions from library_service.py and database.py.
<br><br>

### Summary

- add_book_to_catalog(), borrow_book_by_patron(), and return_book_by_patron were tested using a couple valid test cases each as well as invalid test cases to validate requirements in requirements_specification.md.

- calculate_late_fee_for_book() was tested using tests for different fee amount (from none to the cap)

- search_books_in_catalog() was tested using tests for every search method as well as incorrect input (bad search result or wrong ISBN)

- get_patron_status_report() was tested using tests for different kinds of patrons (one with a book, one with no books, one with fees, one with a mix) and testing incorrect input (bad ID)