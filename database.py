
import sqlite3
import csv


# 1. Create Database
def create_database():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            description TEXT,
            amount REAL,
            expense_date TEXT
        )
    """)

    # Check existing table columns
    cursor.execute("PRAGMA table_info(expenses)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add date column if it does not exist
    if "expense_date" not in columns:
        cursor.execute("""
            ALTER TABLE expenses
            ADD COLUMN expense_date TEXT
        """)

    connection.commit()
    connection.close()

    print("Database created successfully!")


# 2. Load CSV Data Only When Database Is Empty
def insert_expenses():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM expenses")
    count = cursor.fetchone()[0]

    if count == 0:
        try:
            with open("data/expenses.csv", "r", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    cursor.execute("""
                        INSERT INTO expenses
                        (category, description, amount, expense_date)
                        VALUES (?, ?, ?, ?)
                    """, (
                        row["category"],
                        row["description"],
                        float(row["amount"]),
                        row.get("expense_date") or None
                    ))

            connection.commit()
            print("Expenses loaded successfully!")

        except (FileNotFoundError, ValueError, KeyError) as error:
            print("CSV loading error:", error)

    else:
        print("Existing expenses found. CSV import skipped.")

    connection.close()


# 3. View All Expenses
def view_expenses():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    print("\nAll Expenses:")

    if rows:
        for row in rows:
            print(row)
    else:
        print("No expenses found.")

    connection.close()

    return rows


# 4. Calculate Total Expenses
def calculate_database_total():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    print("\nTotal Expenses:", total or 0)

    connection.close()

    return total or 0


# 5. Category-wise Total
def category_wise_total():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
    """)

    rows = cursor.fetchall()

    print("\nCategory-wise Expenses:")

    for row in rows:
        print(row[0], ":", row[1])

    connection.close()

    return rows


# 6. Find Biggest Expense
def biggest_database_expense():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM expenses
        ORDER BY amount DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    print("\nBiggest Expense:", result)

    connection.close()

    return result


# 7. Search by Category
def search_expenses(category):
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM expenses
        WHERE LOWER(category) = LOWER(?)
    """, (category,))

    rows = cursor.fetchall()

    print("\nSearch Results:")

    if rows:
        for row in rows:
            print(row)
    else:
        print("No matching expenses found.")

    connection.close()

    return rows


# 8. Search by Amount
def search_by_amount(minimum_amount):
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE amount >= ?",
        (minimum_amount,)
    )

    rows = cursor.fetchall()

    print("\nSearch Results:")

    if rows:
        for row in rows:
            print(row)
    else:
        print("No matching expenses found.")

    connection.close()

    return rows


# 9. Search by Exact Description
def search_by_description(description):
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE description = ?",
        (description,)
    )

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    connection.close()

    return rows


# 10. Search by Partial Description
def search_partial_description(keyword):
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE description LIKE ?",
        ('%' + keyword + '%',)
    )

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    connection.close()

    return rows


# 11. Add New Expense
def add_expense(category, description, amount, expense_date=None):
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (category, description, amount, expense_date)
        VALUES (?, ?, ?, ?)
    """, (category, description, amount, expense_date))

    connection.commit()
    connection.close()

    print("Expense added successfully!")


# 12. Delete Expense
def delete_expense(expense_id):
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    connection.commit()

    if cursor.rowcount > 0:
        print("Expense deleted successfully!")
    else:
        print("Expense ID not found.")

    connection.close()


# 13. Update Expense
def update_expense(expense_id, new_amount):
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE expenses
        SET amount = ?
        WHERE id = ?
    """, (new_amount, expense_id))

    connection.commit()

    if cursor.rowcount > 0:
        print("Expense updated successfully!")
    else:
        print("Expense ID not found.")

    connection.close()


# 14. Get Expense Details from User
def add_expense_from_user():
    try:
        category = input("Enter category: ").strip()
        description = input("Enter description: ").strip()
        amount = float(input("Enter amount: "))
        expense_date = input("Enter date (YYYY-MM-DD): ").strip()

        if not category or not description:
            print("Category and description cannot be empty!")
            return

        if amount <= 0:
            print("Amount must be positive!")
            return

        from datetime import datetime
        datetime.strptime(expense_date, "%Y-%m-%d")

        add_expense(category, description, amount, expense_date)

    except ValueError:
        print("Enter a valid amount or date in YYYY-MM-DD format!")


# 15. Main Menu
def main_menu():
    while True:
        print("\n========== PyAnalytics ==========")
        print("1. View All Expenses")
        print("2. Add New Expense")
        print("3. Search by Category")
        print("4. Search by Amount")
        print("5. Update Expense")
        print("6. Delete Expense")
        print("7. Calculate Total")
        print("8. Category-wise Total")
        print("9. Find Biggest Expense")
        print("10. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            view_expenses()

        elif choice == "2":
            add_expense_from_user()

        elif choice == "3":
            category = input("Enter category: ").strip()
            search_expenses(category)

        elif choice == "4":
            try:
                amount = float(input("Enter minimum amount: "))
                search_by_amount(amount)
            except ValueError:
                print("Enter a valid amount!")

        elif choice == "5":
            try:
                expense_id = int(input("Enter expense ID: "))
                new_amount = float(input("Enter new amount: "))

                if new_amount <= 0:
                    print("Amount must be positive!")
                else:
                    update_expense(expense_id, new_amount)

            except ValueError:
                print("Enter valid values!")

        elif choice == "6":
            try:
                expense_id = int(input("Enter expense ID: "))
                delete_expense(expense_id)
            except ValueError:
                print("Enter a valid ID!")

        elif choice == "7":
            calculate_database_total()

        elif choice == "8":
            category_wise_total()

        elif choice == "9":
            biggest_database_expense()

        elif choice == "10":
            print("Thank you for using PyAnalytics!")
            break

        else:
            print("Invalid choice! Please enter 1 to 10.")


# 16. Program Starting Point
if __name__ == "__main__":
    create_database()
    insert_expenses()
    main_menu()








