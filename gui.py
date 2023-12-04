from tkinter import *
import sqlite3
from tkinter import messagebox

def execute_query(query, params=None):
    try:
        connection = sqlite3.connect("LibraryDB.db")
        cursor = connection.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        connection.commit()
        result = cursor.fetchall()

        return result

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        connection.close()

def check_out_book():
    book_id = entry_book_id.get()
    borrower_id = entry_borrower_id.get()

    query_add_loan = "INSERT INTO Book_Loan(BookID, BorrowerID, LoanDate, DueDate) VALUES(?, ?, CURRENT_DATE, DATE('now', '+14 days'))"
    query_update_copies = "UPDATE Book_Copies SET No_of_Copies = No_of_Copies - 1 WHERE BookID = ?"

    execute_query(query_add_loan, (book_id, borrower_id))
    execute_query(query_update_copies, (book_id,))

    messagebox.showinfo("Success", "Book checked out successfully!")

def add_borrower():
    borrower_name = entry_borrower_name.get()
    borrower_address = entry_borrower_address.get()
    borrower_phone = entry_borrower_phone.get()

    query_add_borrower = "INSERT INTO Borrower(Name, Address, Phone) VALUES(?, ?, ?)"
    result = execute_query(query_add_borrower, (borrower_name, borrower_address, borrower_phone))

    messagebox.showinfo("Success", f"Borrower added successfully!\nBorrower CardNo: {result[0][0]}")

def add_new_book():
    book_title = entry_book_title.get()
    publisher_id = entry_publisher_id.get()
    author_id = entry_author_id.get()

    query_add_book = "INSERT INTO Book(Title, PublisherID) VALUES(?, ?)"
    result = execute_query(query_add_book, (book_title, publisher_id))

    book_id = result[0][0]

    query_add_book_authors = "INSERT INTO Book_Authors(BookID, AuthorID) VALUES(?, ?)"
    for author in author_id.split(","):
        execute_query(query_add_book_authors, (book_id, author))

    branches = execute_query("SELECT BranchID FROM Library_Branch")
    for branch in branches:
        query_add_book_copies = "INSERT INTO Book_Copies(BookID, BranchID, No_of_Copies) VALUES(?, ?, 5)"
        execute_query(query_add_book_copies, (book_id, branch[0]))

    messagebox.showinfo("Success", f"Book added successfully!\nBook ID: {book_id}")

def list_copies_loan_per_branch():
    book_title = entry_list_copies_loan.get()

    query_list_copies_loan = """
        SELECT B.Title, L.BranchID, COUNT(*) AS CopiesLoaned
        FROM Book_Loan L
        JOIN Book B ON L.BookID = B.BookID
        WHERE B.Title = ?
        GROUP BY B.Title, L.BranchID
    """

    result = execute_query(query_list_copies_loan, (book_title,))

    result_str = "\n".join([f"Branch ID: {row[1]}, Copies Loaned: {row[2]}" for row in result])
    messagebox.showinfo("Copies Loaned per Branch", result_str)

def list_late_returns():
    due_date_start = entry_due_date_start.get()
    due_date_end = entry_due_date_end.get()

    query_late_returns = """
        SELECT BL.BookID, B.Title, BL.BranchID, BL.DateIn, BL.DueDate,
               JULIANDAY(BL.DateIn) - JULIANDAY(BL.DueDate) AS DaysLate
        FROM Book_Loan BL
        JOIN Book B ON BL.BookID = B.BookID
        WHERE BL.DateIn > BL.DueDate
          AND BL.DueDate BETWEEN ? AND ?
    """

    result = execute_query(query_late_returns, (due_date_start, due_date_end))

    result_str = "\n".join([f"Book ID: {row[0]}, Title: {row[1]}, Branch ID: {row[2]}, Days Late: {row[5]}"
                            for row in result])
    messagebox.showinfo("Late Returns", result_str)

def search_borrowers():
    borrower_id = entry_borrower_search_id.get()
    borrower_name = entry_borrower_search_name.get()

    query_search_borrowers = """
        SELECT Borrower.CardNo, Borrower.Name,
               COALESCE(SUM(LateFee), 0) AS LateFeeBalance
        FROM Borrower
        LEFT JOIN Book_Loan ON Borrower.CardNo = Book_Loan.CardNo
        WHERE Borrower.CardNo LIKE ?
           OR Borrower.Name LIKE ?
        GROUP BY Borrower.CardNo, Borrower.Name
        ORDER BY LateFeeBalance
    """

    result = execute_query(query_search_borrowers, (f"%{borrower_id}%", f"%{borrower_name}%"))

    result_str = "\n".join([f"Card No: {row[0]}, Name: {row[1]}, Late Fee Balance: ${row[2]:.2f}"
                            for row in result])
    messagebox.showinfo("Borrowers Search Result", result_str)

def search_books():
    borrower_id = entry_book_search_borrower_id.get()
    book_id = entry_book_search_id.get()
    book_title = entry_book_search_title.get()

    query_search_books = """
        SELECT Borrower.CardNo, Borrower.Name,
               B.BookID, B.Title, COALESCE(LateFee, 'Non-Applicable') AS LateFee
        FROM Book B
        JOIN Book_Loan L ON B.BookID = L.BookID
        JOIN Borrower ON L.CardNo = Borrower.CardNo
        WHERE Borrower.CardNo = ?
           AND (B.BookID LIKE ?
           OR B.Title LIKE ?)
    """

    result = execute_query(query_search_books, (borrower_id, f"%{book_id}%", f"%{book_title}%"))

    result_str = "\n".join([f"Card No: {row[0]}, Name: {row[1]}, Book ID: {row[2]}, Title: {row[3]}, Late Fee: {row[4]}"
                            for row in result])
    messagebox.showinfo("Books Search Result", result_str)

# Create the main window
root = Tk()
root.title("Library Management System")

# Check Out Book Section
frame_check_out = Frame(root)
frame_check_out.grid(row=0, column=0, padx=10, pady=10)

label_book_id = Label(frame_check_out, text="Book ID:")
label_borrower_id = Label(frame_check_out, text="Borrower ID:")

entry_book_id = Entry(frame_check_out)
entry_borrower_id = Entry(frame_check_out)

btn_check_out = Button(frame_check_out, text="Check Out", command=check_out_book)

label_book_id.grid(row=0, column=0, padx=5, pady=5)
label_borrower_id.grid(row=1, column=0, padx=5, pady=5)
entry_book_id.grid(row=0, column=1, padx=5, pady=5)
entry_borrower_id.grid(row=1, column=1, padx=5, pady=5)
btn_check_out.grid(row=2, column=1, pady=10)

# Add Borrower Section
frame_add_borrower = Frame(root)
frame_add_borrower.grid(row=0, column=1, padx=10, pady=10)

label_borrower_name = Label(frame_add_borrower, text="Borrower Name:")
label_borrower_address = Label(frame_add_borrower, text="Borrower Address:")
label_borrower_phone = Label(frame_add_borrower, text="Borrower Phone:")

entry_borrower_name = Entry(frame_add_borrower)
entry_borrower_address = Entry(frame_add_borrower)
entry_borrower_phone = Entry(frame_add_borrower)

btn_add_borrower = Button(frame_add_borrower, text="Add Borrower", command=add_borrower)

label_borrower_name.grid(row=0, column=0, padx=5, pady=5)
label_borrower_address.grid(row=1, column=0, padx=5, pady=5)
label_borrower_phone.grid(row=2, column=0, padx=5, pady=5)
entry_borrower_name.grid(row=0, column=1, padx=5, pady=5)
entry_borrower_address.grid(row=1, column=1, padx=5, pady=5)
entry_borrower_phone.grid(row=2, column=1, padx=5, pady=5)
btn_add_borrower.grid(row=3, column=1, pady=10)

# Add New Book Section
frame_add_book = Frame(root)
frame_add_book.grid(row=1, column=0, padx=10, pady=10)

label_book_title = Label(frame_add_book, text="Book Title:")
label_publisher_id = Label(frame_add_book, text="Publisher ID:")
label_author_id = Label(frame_add_book, text="Author IDs (comma-separated):")

entry_book_title = Entry(frame_add_book)
entry_publisher_id = Entry(frame_add_book)
entry_author_id = Entry(frame_add_book)

btn_add_book = Button(frame_add_book, text="Add Book", command=add_new_book)

label_book_title.grid(row=0, column=0, padx=5, pady=5)
label_publisher_id.grid(row=1, column=0, padx=5, pady=5)
label_author_id.grid(row=2, column=0, padx=5, pady=5)
entry_book_title.grid(row=0, column=1, padx=5, pady=5)
entry_publisher_id.grid(row=1, column=1, padx=5, pady=5)
entry_author_id.grid(row=2, column=1, padx=5, pady=5)
btn_add_book.grid(row=3, column=1, pady=10)

# List Copies Loaned per Branch Section
frame_list_copies_loan = Frame(root)
frame_list_copies_loan.grid(row=1, column=1, padx=10, pady=10)

label_list_copies_loan = Label(frame_list_copies_loan, text="Book Title:")

entry_list_copies_loan = Entry(frame_list_copies_loan)

btn_list_copies_loan = Button(frame_list_copies_loan, text="List Copies Loaned", command=list_copies_loan_per_branch)

label_list_copies_loan.grid(row=0, column=0, padx=5, pady=5)
entry_list_copies_loan.grid(row=0, column=1, padx=5, pady=5)
btn_list_copies_loan.grid(row=1, column=1, pady=10)

# List Late Returns Section
frame_list_late_returns = Frame(root)
frame_list_late_returns.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

label_due_date_start = Label(frame_list_late_returns, text="Due Date Start (YYYY-MM-DD):")
label_due_date_end = Label(frame_list_late_returns, text="Due Date End (YYYY-MM-DD):")

entry_due_date_start = Entry(frame_list_late_returns)
entry_due_date_end = Entry(frame_list_late_returns)

btn_list_late_returns = Button(frame_list_late_returns, text="List Late Returns", command=list_late_returns)

label_due_date_start.grid(row=0, column=0, padx=5, pady=5)
label_due_date_end.grid(row=1, column=0, padx=5, pady=5)
entry_due_date_start.grid(row=0, column=1, padx=5, pady=5)
entry_due_date_end.grid(row=1, column=1, padx=5, pady=5)
btn_list_late_returns.grid(row=2, column=1, pady=10)

# Search Borrowers Section
frame_search_borrowers = Frame(root)
frame_search_borrowers.grid(row=3, column=0, padx=10, pady=10)

label_borrower_search_id = Label(frame_search_borrowers, text="Borrower ID:")
label_borrower_search_name = Label(frame_search_borrowers, text="Borrower Name:")

entry_borrower_search_id = Entry(frame_search_borrowers)
entry_borrower_search_name = Entry(frame_search_borrowers)

btn_search_borrowers = Button(frame_search_borrowers, text="Search Borrowers", command=search_borrowers)

label_borrower_search_id.grid(row=0, column=0, padx=5, pady=5)
label_borrower_search_name.grid(row=1, column=0, padx=5, pady=5)
entry_borrower_search_id.grid(row=0, column=1, padx=5, pady=5)
entry_borrower_search_name.grid(row=1, column=1, padx=5, pady=5)
btn_search_borrowers.grid(row=2, column=1, pady=10)

# Search Books Section
frame_book_search = Frame(root)
frame_book_search.grid(row=3, column=1, padx=10, pady=10)

label_book_search_borrower_id = Label(frame_book_search, text="Borrower ID:")
label_book_search_id = Label(frame_book_search, text="Book ID:")
label_book_search_title = Label(frame_book_search, text="Book Title:")

entry_book_search_borrower_id = Entry(frame_book_search)
entry_book_search_id = Entry(frame_book_search)
entry_book_search_title = Entry(frame_book_search)

btn_search_books = Button(frame_book_search, text="Search Books", command=search_books)

label_book_search_borrower_id.grid(row=0, column=0, padx=5, pady=5)
label_book_search_id.grid(row=1, column=0, padx=5, pady=5)
label_book_search_title.grid(row=2, column=0, padx=5, pady=5)
entry_book_search_borrower_id.grid(row=0, column=1, padx=5, pady=5)
entry_book_search_id.grid(row=1, column=1, padx=5, pady=5)
entry_book_search_title.grid(row=2, column=1, padx=5, pady=5)
btn_search_books.grid(row=3, column=1, pady=10)

# Run the main loop
root.mainloop()
