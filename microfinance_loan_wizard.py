
import sqlite3
import hashlib
import tkinter as tk
from tkinter import messagebox

# Database Setup Functions
def create_database():
    conn = sqlite3.connect('loan_wizard.db')
    cursor = conn.cursor()
    
    # Users table now includes password field
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    
    # Loan amounts, interest rates, repayment schedules, transaction histories
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS LoanAmounts (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS InterestRates (
        interest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER,
        rate REAL NOT NULL,
        FOREIGN KEY (loan_id) REFERENCES LoanAmounts(loan_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS RepaymentSchedules (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER,
        due_date TEXT NOT NULL,
        FOREIGN KEY (loan_id) REFERENCES LoanAmounts(loan_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS TransactionHistories (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER,
        transaction_date TEXT NOT NULL,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL,
        FOREIGN KEY (loan_id) REFERENCES LoanAmounts(loan_id)
    )
    ''')

    conn.commit()
    conn.close()

# User Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password):
    conn = sqlite3.connect('loan_wizard.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO Users (name, email, password) VALUES (?, ?, ?)
        ''', (name, email, hash_password(password)))
        
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect('loan_wizard.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT user_id FROM Users WHERE email = ? AND password = ?
    ''', (email, hash_password(password)))
    
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# UI Functions
def register_interface():
    def register_user_ui():
        name = name_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        if name and email and password:
            user_id = register_user(name, email, password)
            if user_id:
                messagebox.showinfo("Success", "User registered successfully!")
                window.destroy()  # Close the registration window
            else:
                messagebox.showwarning("Error", "Email already exists.")
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    window = tk.Tk()
    window.title("Loan Wizard - Register User")

    tk.Label(window, text="Name:").grid(row=0, column=0)
    name_entry = tk.Entry(window)
    name_entry.grid(row=0, column=1)

    tk.Label(window, text="Email:").grid(row=1, column=0)
    email_entry = tk.Entry(window)
    email_entry.grid(row=1, column=1)

    tk.Label(window, text="Password:").grid(row=2, column=0)
    password_entry = tk.Entry(window, show="*")
    password_entry.grid(row=2, column=1)

    tk.Button(window, text="Register", command=register_user_ui).grid(row=3, columnspan=2)

    window.mainloop()

def login_interface():
    def login_user_ui():
        email = email_entry.get()
        password = password_entry.get()
        user_id = login_user(email, password)
        if user_id:
            messagebox.showinfo("Success", f"Logged in as User ID: {user_id}")
            window.destroy()  # Close the login window
            main_application(user_id)  # Open the main application for this user
        else:
            messagebox.showwarning("Error", "Invalid email or password.")

    window = tk.Tk()
    window.title("Loan Wizard - Login")

    tk.Label(window, text="Email:").grid(row=0, column=0)
    email_entry = tk.Entry(window)
    email_entry.grid(row=0, column=1)

    tk.Label(window, text="Password:").grid(row=1, column=0)
    password_entry = tk.Entry(window, show="*")
    password_entry.grid(row=1, column=1)

    tk.Button(window, text="Login", command=login_user_ui).grid(row=2, columnspan=2)

    window.mainloop()

def main_application(user_id):
    window = tk.Tk()
    window.title("Loan Wizard - User Dashboard")
    
    main_frame = tk.Frame(window)
    main_frame.pack(padx=10, pady=10)

    tk.Label(main_frame, text=f"Welcome User ID: {user_id}", font=("Helvetica", 16)).pack(pady=(0, 10))

    tk.Button(main_frame, text="Make Repayment", command=lambda: repayment_interface()).pack(pady=5)
    tk.Button(main_frame, text="View Transactions", command=lambda: view_transactions(user_id)).pack(pady=5)

    window.mainloop()

def view_transactions(user_id):
    conn = sqlite3.connect('loan_wizard.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT la.loan_id, th.transaction_date, th.amount, th.transaction_type
    FROM TransactionHistories th
    JOIN LoanAmounts la ON th.loan_id = la.loan_id
    WHERE la.user_id = ?
    ''', (user_id,))
    
    transactions = cursor.fetchall()
    conn.close()

    transaction_window = tk.Toplevel()
    transaction_window.title("Transaction History")

    for transaction in transactions:
        tk.Label(transaction_window, text=f"Loan ID: {transaction[0]}, Date: {transaction[1]}, Amount: {transaction[2]}, Type: {transaction[3]}").pack()
    
    if not transactions:
        tk.Label(transaction_window, text="No transactions found.").pack()

# Main execution
if __name__ == "__main__":
    create_database()  # Create the database and tables
    login_interface()  # Launch the login interface
    # Optionally launch the registration interface if needed
    # register_interface()
