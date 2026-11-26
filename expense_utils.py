
class Expense:

    def __init__(self, category, description, amount):
        self.category = category
        self.description = description
        self.amount = amount

    def display(self):
        print("Category:", self.category)
        print("Description:", self.description)
        print("Amount:", self.amount)
        print("-------------------")


def calculate_total(expenses):
    total = 0

    for expense in expenses:
        total += expense.amount

    return total
