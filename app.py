
import sqlite3
import csv
import io
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, Response, make_response

app = Flask(__name__)

DATABASE = "expenses.db"


# 1. Connect to the existing database
def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# 2. Get all expenses
def get_all_expenses():
    connection = get_connection()
    expenses = connection.execute(
        "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC"
    ).fetchall()
    connection.close()
    return expenses


# 3. Calculate total expenses
def get_total_expenses():
    connection = get_connection()
    result = connection.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses"
    ).fetchone()
    connection.close()
    return result["total"]


# 4. Get category-wise totals
def get_category_totals():
    connection = get_connection()
    categories = connection.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()
    connection.close()
    return categories


# 5. Get expense statistics
def get_expense_statistics():
    connection = get_connection()
    result = connection.execute("""
        SELECT
            COUNT(*) AS count,
            COALESCE(MAX(amount), 0) AS highest,
            COALESCE(MIN(amount), 0) AS lowest,
            COALESCE(AVG(amount), 0) AS average
        FROM expenses
    """).fetchone()
    connection.close()

    return {
        "count": result["count"],
        "highest": result["highest"],
        "lowest": result["lowest"],
        "average": result["average"],

        # Compatibility aliases
        "total_count": result["count"],
        "highest_amount": result["highest"],
        "lowest_amount": result["lowest"],
        "average_amount": result["average"]
    }


# 6. Get monthly expense totals
def get_monthly_totals():
    connection = get_connection()
    monthly_totals = connection.execute("""
        SELECT
            strftime('%Y-%m', expense_date) AS month,
            SUM(amount) AS total
        FROM expenses
        WHERE expense_date IS NOT NULL
          AND expense_date != ''
        GROUP BY strftime('%Y-%m', expense_date)
        ORDER BY month
    """).fetchall()
    connection.close()
    return monthly_totals


# 7. Create the PDF using built-in Python code
def pdf_escape(value):
    value = str(value)
    value = value.encode("ascii", "replace").decode("ascii")
    value = value.replace("\\", "\\\\")
    value = value.replace("(", "\\(")
    value = value.replace(")", "\\)")
    return value


def create_pdf(lines):
    content = ["BT", "/F1 10 Tf", "50 790 Td"]

    for index, line in enumerate(lines):
        if index > 0:
            content.append("0 -16 Td")

        content.append(f"({pdf_escape(line)}) Tj")

    content.append("ET")
    stream = "\n".join(content).encode("ascii")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") +
        b" >>\nstream\n" + stream + b"\nendstream"
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(
            f"{number} 0 obj\n".encode("ascii")
            + obj
            + b"\nendobj\n"
        )

    xref_position = len(pdf)

    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_position}\n%%EOF".encode("ascii")
    )

    return bytes(pdf)


# 8. Dashboard
@app.route("/")
def index():
    search_category = request.args.get("category", "").strip()
    minimum_amount = request.args.get("min_amount", "").strip()

    connection = get_connection()

    query = "SELECT * FROM expenses WHERE 1=1"
    parameters = []

    if search_category:
        query += " AND category LIKE ?"
        parameters.append(f"%{search_category}%")

    if minimum_amount:
        try:
            minimum_value = float(minimum_amount)
            query += " AND amount >= ?"
            parameters.append(minimum_value)
        except ValueError:
            minimum_amount = ""

    query += " ORDER BY expense_date DESC, id DESC"

    expenses = connection.execute(query, parameters).fetchall()
    connection.close()

    total = get_total_expenses()
    categories = get_category_totals()
    statistics = get_expense_statistics()
    monthly_totals = get_monthly_totals()

    chart_labels = [item["category"] for item in categories]
    chart_values = [item["total"] for item in categories]

    monthly_labels = [item["month"] for item in monthly_totals]
    monthly_values = [item["total"] for item in monthly_totals]

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        categories=categories,
        statistics=statistics,
        chart_labels=chart_labels,
        chart_values=chart_values,
        monthly_labels=monthly_labels,
        monthly_values=monthly_values,
        monthly_totals=monthly_totals,
        search_category=search_category,
        minimum_amount=minimum_amount,
        error_message=""
    )


# 9. Add a new expense
@app.route("/add", methods=["POST"])
def add():
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    amount_text = request.form.get("amount", "").strip()
    expense_date = request.form.get("expense_date", "").strip()

    try:
        amount = float(amount_text)

        if not category or not description or amount <= 0:
            return "Please enter valid expense details.", 400

        if not expense_date:
            expense_date = date.today().isoformat()

        connection = get_connection()
        connection.execute("""
            INSERT INTO expenses
            (category, description, amount, expense_date)
            VALUES (?, ?, ?, ?)
        """, (category, description, amount, expense_date))
        connection.commit()
        connection.close()

        return redirect(url_for("index"))

    except ValueError:
        return "Please enter a valid amount.", 400


# 10. Delete an expense
@app.route("/delete/<int:expense_id>", methods=["POST", "GET"])
def delete(expense_id):
    connection = get_connection()
    connection.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )
    connection.commit()
    connection.close()

    return redirect(url_for("index"))


# 11. Edit an expense
@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit(expense_id):
    connection = get_connection()

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        amount_text = request.form.get("amount", "").strip()
        expense_date = request.form.get("expense_date", "").strip()

        try:
            amount = float(amount_text)

            if not category or not description or amount <= 0:
                connection.close()
                return "Please enter valid expense details.", 400

            connection.execute("""
                UPDATE expenses
                SET category = ?,
                    description = ?,
                    amount = ?,
                    expense_date = ?
                WHERE id = ?
            """, (
                category,
                description,
                amount,
                expense_date,
                expense_id
            ))

            connection.commit()
            connection.close()

            return redirect(url_for("index"))

        except ValueError:
            connection.close()
            return "Please enter a valid amount.", 400

    expense = connection.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    ).fetchone()

    connection.close()

    if expense is None:
        return "Expense not found.", 404

    return render_template("edit.html", expense=expense)


# 12. Export expenses as CSV
@app.route("/export")
def export_csv():
    expenses = get_all_expenses()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Category",
        "Description",
        "Amount",
        "Expense Date"
    ])

    for expense in expenses:
        writer.writerow([
            expense["id"],
            expense["category"],
            expense["description"],
            expense["amount"],
            expense["expense_date"]
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = (
        "attachment; filename=expenses_report.csv"
    )
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    return response


# 13. Export expenses as PDF
@app.route("/export-pdf")
def export_pdf():
    expenses = get_all_expenses()

    lines = [
        "PYANALYTICS - EXPENSE REPORT",
        "----------------------------------------",
        f"Total Expenses: {len(expenses)}",
        f"Total Amount: Rs. {get_total_expenses():.2f}",
        "----------------------------------------",
        "ID | Category | Description | Amount | Date",
        "----------------------------------------"
    ]

    for expense in expenses:
        line = (
            f"{expense['id']} | "
            f"{expense['category']} | "
            f"{expense['description']} | "
            f"Rs. {expense['amount']:.2f} | "
            f"{expense['expense_date']}"
        )
        lines.append(line[:100])

    pdf_data = create_pdf(lines)

    response = make_response(pdf_data)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        "attachment; filename=expenses_report.pdf"
    )

    return response


# 14. Run Flask application
if __name__ == "__main__":
    app.run(debug=True)
