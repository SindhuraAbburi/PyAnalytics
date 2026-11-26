import sqlite3
import database
import pytest
import app as flask_app



def test_create_database(tmp_path, monkeypatch):
    test_db = tmp_path / "test_expenses.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    connection = original_connect(test_db)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='expenses'
    """)

    result = cursor.fetchone()
    connection.close()

    assert result is not None
    assert result[0] == "expenses"


def test_add_expense(tmp_path, monkeypatch):
    test_db = tmp_path / "test_expenses.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")

    connection = original_connect(test_db)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, description, amount, expense_date
        FROM expenses
    """)

    result = cursor.fetchone()
    connection.close()

    assert result == ("Food", "Lunch", 150.0, "2026-11-25")


def test_delete_expense(tmp_path, monkeypatch):
    test_db = tmp_path / "test_delete.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")

    connection = original_connect(test_db)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM expenses")
    expense_id = cursor.fetchone()[0]
    connection.close()

    database.delete_expense(expense_id)

    connection = original_connect(test_db)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM expenses")
    count = cursor.fetchone()[0]
    connection.close()

    assert count == 0


def test_update_expense(tmp_path, monkeypatch):
    test_db = tmp_path / "test_update.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")

    connection = original_connect(test_db)
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM expenses")
    expense_id = cursor.fetchone()[0]
    connection.close()

    database.update_expense(expense_id, 200.0)

    connection = original_connect(test_db)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT amount FROM expenses WHERE id = ?",
        (expense_id,)
    )
    result = cursor.fetchone()
    connection.close()

    assert result[0] == 200.0

def test_view_expenses(tmp_path, monkeypatch):
    test_db = tmp_path / "test_view.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")

    expenses = database.view_expenses()

    assert len(expenses) == 1
    assert expenses[0][1] == "Food"
    assert expenses[0][2] == "Lunch"
    assert expenses[0][3] == 150.0


def test_calculate_database_total(tmp_path, monkeypatch):
    test_db = tmp_path / "test_total.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")
    database.add_expense("Travel", "Bus", 50.0, "2026-11-25")

    total = database.calculate_database_total()

    assert total == 200.0


def test_category_wise_total(tmp_path, monkeypatch):
    test_db = tmp_path / "test_category.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")
    database.add_expense("Food", "Dinner", 100.0, "2026-11-25")
    database.add_expense("Travel", "Bus", 50.0, "2026-11-25")

    result = database.category_wise_total()

    assert ("Food", 250.0) in result
    assert ("Travel", 50.0) in result


def test_biggest_database_expense(tmp_path, monkeypatch):
    test_db = tmp_path / "test_biggest.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")
    database.add_expense("Travel", "Bus", 50.0, "2026-11-25")
    database.add_expense("Shopping", "Books", 500.0, "2026-11-25")

    result = database.biggest_database_expense()

    assert result[1] == "Shopping"
    assert result[2] == "Books"
    assert result[3] == 500.0


def test_search_expenses(tmp_path, monkeypatch):
    test_db = tmp_path / "test_search.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")
    database.add_expense("Food", "Dinner", 100.0, "2026-11-25")
    database.add_expense("Travel", "Bus", 50.0, "2026-11-25")

    result = database.search_expenses("Food")

    assert len(result) == 2
    assert all(row[1] == "Food" for row in result)


def test_search_by_amount(tmp_path, monkeypatch):
    test_db = tmp_path / "test_amount.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")
    database.add_expense("Travel", "Bus", 50.0, "2026-11-25")
    database.add_expense("Shopping", "Books", 500.0, "2026-11-25")

    result = database.search_by_amount(100.0)

    assert len(result) == 2
    assert all(row[3] >= 100.0 for row in result)


def test_search_by_description(tmp_path, monkeypatch):
    test_db = tmp_path / "test_description.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")
    database.add_expense("Food", "Dinner", 100.0, "2026-11-25")
    database.add_expense("Travel", "Bus", 50.0, "2026-11-25")

    result = database.search_by_description("Lunch")

    assert len(result) == 1
    assert result[0][2] == "Lunch"
    assert result[0][3] == 150.0


def test_search_partial_description(tmp_path, monkeypatch):
    test_db = tmp_path / "test_partial.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Lunch", 150.0, "2026-11-25")
    database.add_expense("Food", "Dinner", 100.0, "2026-11-25")
    database.add_expense("Travel", "Bus", 50.0, "2026-11-25")

    result = database.search_partial_description("Lun")

    assert len(result) == 1
    assert result[0][2] == "Lunch"


def test_add_expense_without_date(tmp_path, monkeypatch):
    test_db = tmp_path / "test_no_date.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Snacks", 80.0)

    connection = original_connect(test_db)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT category, description, amount, expense_date FROM expenses"
    )
    result = cursor.fetchone()

    connection.close()

    assert result == ("Food", "Snacks", 80.0, None)


def test_add_expense_with_zero_amount(tmp_path, monkeypatch):
    test_db = tmp_path / "test_zero.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Free Snack", 0.0)

    connection = original_connect(test_db)
    cursor = connection.cursor()

    cursor.execute("SELECT amount FROM expenses")
    result = cursor.fetchone()

    connection.close()

    assert result[0] == 0.0


def test_add_expense_with_negative_amount(tmp_path, monkeypatch):
    test_db = tmp_path / "test_negative.db"
    original_connect = sqlite3.connect

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: original_connect(test_db)
    )

    database.create_database()

    database.add_expense("Food", "Test Expense", -50.0)

    connection = original_connect(test_db)
    cursor = connection.cursor()

    cursor.execute("SELECT amount FROM expenses")
    result = cursor.fetchone()

    connection.close()

    assert result[0] == -50.0

# Flask test database fixture
@pytest.fixture
def flask_client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_flask.db"

    monkeypatch.setattr(
        flask_app,
        "DATABASE",
        str(test_db)
    )

    flask_app.app.config["TESTING"] = True

    connection = sqlite3.connect(test_db)

    connection.execute("""
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            description TEXT,
            amount REAL,
            expense_date TEXT
        )
    """)

    connection.commit()
    connection.close()

    with flask_app.app.test_client() as client:
        yield client


# 16. Test Flask dashboard
def test_flask_dashboard(flask_client):
    response = flask_client.get("/")
    assert response.status_code == 200


# 17. Test Flask add expense
def test_flask_add_expense(flask_client, tmp_path):
    response = flask_client.post("/add", data={
        "category": "Food",
        "description": "Test Lunch",
        "amount": "150",
        "expense_date": "2026-11-25"
    })

    assert response.status_code == 302

    connection = sqlite3.connect(tmp_path / "test_flask.db")
    result = connection.execute(
        "SELECT category, description, amount, expense_date FROM expenses"
    ).fetchone()
    connection.close()

    assert result == ("Food", "Test Lunch", 150.0, "2026-11-25")


# 18. Test Flask invalid amount
def test_flask_invalid_amount(flask_client):
    response = flask_client.post("/add", data={
        "category": "Food",
        "description": "Lunch",
        "amount": "abc",
        "expense_date": "2026-11-25"
    })

    assert response.status_code == 400


# 19. Test Flask missing category
def test_flask_missing_category(flask_client):
    response = flask_client.post("/add", data={
        "category": "",
        "description": "Lunch",
        "amount": "150",
        "expense_date": "2026-11-25"
    })

    assert response.status_code == 400


# 20. Test Flask missing description
def test_flask_missing_description(flask_client):
    response = flask_client.post("/add", data={
        "category": "Food",
        "description": "",
        "amount": "150",
        "expense_date": "2026-11-25"
    })

    assert response.status_code == 400

