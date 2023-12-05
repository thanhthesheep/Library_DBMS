# import tkinter
from tkinter import *
import sqlite3
from tkinter import messagebox
# import csv

def execute_query(query, params=None):
    try:
        connection = sqlite3.connect("D:\School\Online classes\Fall 2023\CSE3330\Project_2\Library.db") 
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

    connection = sqlite3.connect("D:\School\Online classes\Fall 2023\CSE3330\Project_2\Library.db")
    cursor = connection.cursor()

    book_id = entry_book_id.get()
    borrower_id = entry_branch_id.get()
    card_no = entry_card_number.get()


    query_neg = '''
        SELECT B.No_Of_Copies
        FROM BOOK_COPIES B
        WHERE B.Book_Id = ?
    '''
    
    cursor.execute(query_neg, (book_id,))

    result = cursor.fetchall()
    # print("This is something")
    if result[0][0] <= 0:
        print("No books left to checkout")
    else:

        query_add_loan = "INSERT INTO BOOK_LOANS(Book_Id, Branch_Id, Card_no, Date_out, Due_date) VALUES(?, ?, ? , CURRENT_DATE, DATE('now', '+14 days'))"

        query_check_num = '''
            SELECT B.No_Of_Copies
            FROM BOOK_COPIES B
            WHERE B.Book_Id = ? AND B.Branch_Id = ?
        '''

        cursor.execute(query_add_loan, (book_id, borrower_id, card_no))
        cursor.execute(query_check_num, (book_id,borrower_id))

        result = cursor.fetchall()
        connection.commit()


    messagebox.showinfo("Success", "Book checked out successfully!")
    print(result)
    connection.close()

def add_borrower():
    connection = sqlite3.connect("D:\School\Online classes\Fall 2023\CSE3330\Project_2\Library.db")
    cursor = connection.cursor()

    borrower_name = entry_borrower_name.get()
    borrower_address = entry_borrower_address.get()
    borrower_phone = entry_borrower_phone.get()

    query_add_borrowers = '''INSERT INTO BORROWER(Name, Address, Phone) VALUES(?, ?, ?)'''
    
    # Correct placement of parameters
    cursor.execute(query_add_borrowers, (borrower_name, borrower_address, borrower_phone))

    # Commit changes to the database
    connection.commit()

    # Retrieve the last inserted row ID (CardNo)
    borrower_card_no = cursor.lastrowid

    # Display success message
    messagebox.showinfo("Success", f"Borrower added successfully!\nBorrower CardNo: {borrower_card_no}")

    # Close the database connection
    connection.close()

def add_new_book():
    connection = sqlite3.connect("D:\School\Online classes\Fall 2023\CSE3330\Project_2\Library.db")
    cursor = connection.cursor()

    book_title = entry_book_title.get()
    book_id = entry_publisher_id.get()
    publisher_name = entry_publisher_name.get()
    author_name = entry_author_name.get()

    # Insert the book details into the BOOK table
    query_add_book = '''INSERT INTO BOOK(Book_Id, Title, Publisher_Name) VALUES (?, ?, ?)'''

    # Execute the query to add the book details
    cursor.execute(query_add_book, (book_id,book_title, publisher_name,))



    # Retrieve the last inserted row ID (Book_Id)
    # book_id = cursor.lastrowid

    # Insert book authors into the BOOK_AUTHORS table
    query_add_book_authors = '''INSERT INTO BOOK_AUTHORS(Book_Id, Author_Name) VALUES(?, ?)'''

    cursor.execute(query_add_book_authors, (book_id, author_name,))  # strip to remove leading/trailing spaces


    # Insert book copies into the BOOK_COPIES table for each library branch
    # branches = execute_query("SELECT Branch_Id FROM Library_Branch")
   
    query_add_book_copies = '''INSERT INTO BOOK_COPIES(Book_Id, Branch_Id, No_Of_Copies) VALUES 
        (?, 1, 5)
        '''
    cursor.execute(query_add_book_copies, (book_id,))
    query_add_book_copies = '''INSERT INTO BOOK_COPIES(Book_Id, Branch_Id, No_Of_Copies) VALUES 
    (?, 2, 5)
    '''
    cursor.execute(query_add_book_copies, (book_id,))
    query_add_book_copies = '''INSERT INTO BOOK_COPIES(Book_Id, Branch_Id, No_Of_Copies) VALUES 
    (?, 3, 5)
    '''
    cursor.execute(query_add_book_copies, (book_id,))
    query_add_book_copies = '''INSERT INTO BOOK_COPIES(Book_Id, Branch_Id, No_Of_Copies) VALUES 
    (?, 4, 5)
    '''
    cursor.execute(query_add_book_copies, (book_id,))
    query_add_book_copies = '''INSERT INTO BOOK_COPIES(Book_Id, Branch_Id, No_Of_Copies) VALUES 
    (?, 5, 5)
    '''
    cursor.execute(query_add_book_copies, (book_id,))
    

    # Commit changes to the database
    connection.commit()

    # Display success message
    messagebox.showinfo("Success", f"Book added successfully!\nBook ID: {book_id}")

    # Close the database connection
    connection.close()

def list_copies_loan_per_branch():
    book_title = entry_list_copies_loan.get()

    query_list_copies_loan = '''
        SELECT B.Title, L.Branch_Id, COUNT(*) AS CopiesLoaned
        FROM Book_Loans L
        JOIN Book B ON L.Book_Id = B.Book_Id
        WHERE B.Title = ?
        GROUP BY B.Title, L.Branch_Id
    '''

    result = execute_query(query_list_copies_loan, (book_title,))
    formatted_result = "\n".join([f"Title: {row[0]}, Branch ID: {row[1]}, Copies Loaned: {row[2]}" for row in result])
    messagebox.showinfo("Copies Loaned per Branch", formatted_result)

def list_late_returns():
    connection = sqlite3.connect("D:\School\Online classes\Fall 2023\CSE3330\Project_2\Library.db")
    cursor = connection.cursor()  

    due_date_start = entry_due_date_start.get()
    due_date_end = entry_due_date_end.get()

    query_late_returns = '''
        SELECT B.Title, julianday(BL.Returned_date) - julianday(BL.Due_Date) AS DaysLate
        FROM BOOK_LOANS BL NATURAL JOIN BOOK B 
        WHERE BL.Due_Date BETWEEN ? AND ?
    '''

    cursor.execute(query_late_returns, (due_date_start, due_date_end))

    # result_str = "\n".join([f"Book ID: {row[0]}, Title: {row[1]}, Branch ID: {row[2]}, Days Late: {row[5]}"
    #                         for row in result])

    result = cursor.fetchall()
    connection.commit()
    formatted_result = "\n".join([f"{row[0]} - {row[1]} days late" for row in result])
    messagebox.showinfo("Late Returns", formatted_result)

def search_borrowers():
    connection = sqlite3.connect("D:\School\Online classes\Fall 2023\CSE3330\Project_2\Library.db") 
    cursor = connection.cursor()

    borrower_id = entry_borrower_search_id.get()
    borrower_name = entry_borrower_search_name.get()

    # Case No info provided
    if borrower_id == "" and borrower_name == "":
       query_no_info = '''
       SELECT B.Card_No, B.Name,(CASE 
            WHEN julianday(BL.Returned_date) - julianday(BL.Due_Date) > 0 
            THEN SUM(LB.LateFee * (julianday(BL.Returned_date) - julianday(BL.Due_Date))) ELSE 0 END) AS LateFeeBalance 
        FROM BORROWER B JOIN BOOK_LOANS BL ON B.Card_No = BL.Card_No JOIN LIBRARY_BRANCH LB ON BL.Branch_Id = LB.Branch_Id
        GROUP BY B.Card_No, B.Name
        ORDER BY LateFeeBalance'''     
       cursor.execute(query_no_info)
       result = cursor.fetchall()
       formatted_result = "\n".join([f"Card No: {row[0]}, Name: {row[1]}, Late Fee Balance: {'{:.2f}'.format(row[2]) if row[2] is not None else '0.00'}" for row in result])
       messagebox.showinfo("Borrowers Result", formatted_result)
    else:
        query_search_borrowers = '''
            SELECT B.Card_No, B.Name, (CASE 
                WHEN julianday(BL.Returned_date) - julianday(BL.Due_Date) > 0 
                THEN SUM(LB.LateFee * (julianday(BL.Returned_date) - julianday(BL.Due_Date))) ELSE 0 END) AS LateFeeBalance  
           FROM BORROWER B JOIN BOOK_LOANS BL ON B.Card_No = BL.Card_No JOIN LIBRARY_BRANCH LB ON BL.Branch_Id = LB.Branch_Id
            WHERE B.Card_No LIKE ?
            OR B.Name LIKE ?
            GROUP BY B.Card_No, B.Name
        '''
        cursor.execute(query_search_borrowers, (borrower_id,f"%{borrower_name}%"))

        result = cursor.fetchall()

        formatted_result = "\n".join([f"Card No: {row[0]}, Name: {row[1]}, Late Fee Balance: {'{:.2f}'.format(row[2]) if row[2] is not None else '0.00'}" for row in result])
        messagebox.showinfo("Borrowers Result", formatted_result)



def search_books():
    connection = sqlite3.connect("D:\School\Online classes\Fall 2023\CSE3330\Project_2\Library.db") 
    cursor = connection.cursor()

    borrower_id = entry_book_search_borrower_id.get()
    book_id = entry_book_search_id.get()
    book_title = entry_book_search_title.get()


    query_search_books = '''
            SELECT BR.Name, B.Title, (CASE 
                WHEN julianday(BL.Returned_date) - julianday(BL.Due_Date) > 0 
                THEN CAST(LB.LateFee * (julianday(BL.Returned_date) - julianday(BL.Due_Date)) AS TEXT) ELSE 'Not-Applicable' END) AS LateFeeBalance
            FROM BOOK B
            JOIN BOOK_LOANS BL ON B.Book_Id = BL.Book_Id
            JOIN BORROWER BR ON BL.Card_No = BR.Card_No
            JOIN LIBRARY_BRANCH LB ON BL.Branch_Id = LB.Branch_Id
            WHERE BR.Card_No = ?
            AND (B.Book_Id LIKE ?
            OR B.Title LIKE ?)
    '''
    cursor.execute(query_search_books, (borrower_id, book_id, f"%{book_title}%"))


    result = cursor.fetchall()
    # result_str = "\n".join([f"Card No: {row[0]}, Name: {row[1]}, Book ID: {row[2]}, Title: {row[3]}, Late Fee: {row[4]}"
    #                         for row in result])
    formatted_result = "\n".join([f"Name: {row[0]}, Title: {row[1]}, Late Fee Balance: {row[2]}" for row in result])
    messagebox.showinfo("Books Search Result", formatted_result)
# Create the main window

root = Tk()
root.title("Library Management System")

library_db_connect = sqlite3.connect("D:\School\Online classes\Fall 2023\CSE3330\Project_2\Library.db")
library_db_cursor = library_db_connect.cursor()

# Create the tables

# create_book = """CREATE TABLE IF NOT EXIST BOOK(Book_Id INT NOT NULL,
#     Title VARCHAR(70),
#     Publisher_Name VARCHAR(50),
#     PRIMARY KEY(Book_Id),
#     FOREIGN KEY(Publisher_Name) REFERENCES PUBLISHER(Publisher_Name));"""


# library_db_cursor.execute(create_book)

# create_borrower = """CREATE TABLE IF NOT EXIST BORROWER(
# Card_No INTEGER PRIMARY KEY AUTOINCREMENT,
# Name VARCHAR(70) NOT NULL,
# Address VARCHAR(70),
# Phone VARCHAR(12) NOT NULL);
# """

# library_db_cursor.execute(create_borrower)

# create_publisher = """CREATE TABLE IF NOT EXIST PUBLISHER(
# Publisher_Name VARCHAR(50),
# Phone VARCHAR(12) NOT NULL,
# Address VARCHAR(100),
# PRIMARY KEY(Publisher_Name)
# );
# """

# library_db_cursor.execute(ceate_publisher)

# create_library_branch = """CREATE TABLE IF NOT EXIST LIBRARY_BRANCH(
# Branch_Id INT NOT NULL,
# Branch_Name VARCHAR(70),
# Branch_Adress VarChar(70),
# PRIMARY KEY(Branch_Id)r
# );
# """

# library_db_cursor.execute(create_library_branch)

# create_book_loans = """CREATE TABLE IF NOT EXIST BOOK_LOANS(
# Book_Id INT NOT NULL,
# Branch_Id INT NOT NULL,
# Card_No CHAR(6),
# Date_Out DATE,
# Due_Date DATE,
# Returned_date DATE,
# PRIMARY KEY(Book_Id,Branch_Id,Card_No)
# FOREIGN KEY(Book_Id) REFERENCES BOOK(Book_Id)
# FOREIGN KEY(Branch_Id) REFERENCES LIBRARY_BRANCH(Branch_Id)
# FOREIGN KEY(Card_No) REFERENCES BORROWER(Card_No)
# );
# """

# library_db_cursor.execute(create_book_loans)

# create_book_copies = """CREATE TABLE IF NOT EXIST BOOK_COPIES(
# Book_Id INT NOT NULL,
# Branch_Id INT NOT NULL,
# No_Of_Copies INT NOT NULL,

# PRIMARY KEY(Book_Id,Branch_Id)
# FOREIGN KEY(Book_Id) REFERENCES BOOK(Book_Id)
# FOREIGN KEY(Branch_Id) REFERENCES LIBRARY_BRANCH(Branch_Id)
# );
# """

# library_db_cursor.execute(create_book_copies)

# create_book_authors = """CREATE TABLE IF NOT EXIST BOOK_AUTHORS(
# Book_Id INT NOT NULL,
# Author_Name VARCHAR(50),
# PRIMARY KEY(Book_Id)
# FOREIGN KEY(Book_Id) REFERENCES BOOK(Book_Id)
# );
# """
# library_db_cursor.execute(create_book_authors)
############################################################################################################

library_db_connect.commit()
# Check Out Book Section
frame_check_out = Frame(root)
frame_check_out.grid(row=0, column=0, padx=10, pady=10)

label_book_id = Label(frame_check_out, text="Book ID:")
label_branch_id = Label(frame_check_out, text="Branch ID:")
label_card_number = Label(frame_check_out, text="Card Number:")

entry_book_id = Entry(frame_check_out)
entry_branch_id = Entry(frame_check_out)
entry_card_number = Entry(frame_check_out)

btn_check_out = Button(frame_check_out, text="Check Out", command=check_out_book)

label_book_id.grid(row=0, column=0, padx=5, pady=5)
label_branch_id.grid(row=1, column=0, padx=5, pady=5)
label_card_number.grid(row=2, column=0, padx=5, pady=5)

entry_book_id.grid(row=0, column=1, padx=5, pady=5)
entry_branch_id.grid(row=1, column=1, padx=5, pady=5)
entry_card_number.grid(row=2, column=1, padx=5, pady=5)

btn_check_out.grid(row=3, column=1, pady=10)

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
label_book_id = Label(frame_add_book, text="Book ID:")
label_author_name = Label(frame_add_book, text="Author Name (comma-separated):")
label_publisher_name = Label(frame_add_book, text="Publisher Name:")

entry_book_title = Entry(frame_add_book)
entry_publisher_id = Entry(frame_add_book)
entry_author_name = Entry(frame_add_book)
entry_publisher_name = Entry(frame_add_book)

btn_add_book = Button(frame_add_book, text="Add Book", command=add_new_book)

label_book_title.grid(row=0, column=0, padx=5, pady=5)
label_book_id.grid(row=1, column=0, padx=5, pady=5)
label_author_name.grid(row=2, column=0, padx=5, pady=5)
label_publisher_name.grid(row=3, column=0, padx=5, pady=5)
entry_book_title.grid(row=0, column=1, padx=5, pady=5)
entry_publisher_id.grid(row=1, column=1, padx=5, pady=5)
entry_author_name.grid(row=2, column=1, padx=5, pady=5)
entry_publisher_name.grid(row=3, column=1, padx=5, pady=5)
btn_add_book.grid(row=4, column=1, pady=10)

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
