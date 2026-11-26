
import csv
from expense_utils import Expense, calculate_total

expenses = []

with open("data/expenses.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        expense = Expense(
            row["category"],
            row["description"],
            int(row["amount"])
        )

        expenses.append(expense)

print("All Expenses:")

for expense in expenses:
    expense.display()

total = calculate_total(expenses)

print("Total Expenses:", total)
