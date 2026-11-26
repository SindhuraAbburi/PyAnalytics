# PyAnalytics – Expense Management and Data Analytics Dashboard

## Project Overview
PyAnalytics is a Python-based expense management and data analytics application. It allows users to add, view, edit, delete, search, and analyze expenses through a web dashboard.

## Technologies Used
- Python
- Flask
- SQLite
- HTML and CSS
- CSV
- Chart.js
- Pytest

## Features
- Read and process CSV files
- Calculate total and category-wise expenses
- Store expense records using SQLite
- Add, update, delete, and search expenses
- Flask web dashboard
- Monthly expense summaries and charts
- Export expenses to CSV and PDF
- Automated testing using Pytest

## Project Structure
```text
PyAnalytics/
├── app.py
├── main.py
├── database.py
├── expense_utils.py
├── test_database.py
├── README.md
├── data/
│   └── expenses.csv
└── templates/
    ├── index.html
    └── edit.html
```

## How to Run
1. Install Python.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run the application using `python app.py`.
4. Open the local Flask address shown in the terminal.

## Run Automated Tests
```bash
python -m pytest -v
```

## Project Status
Four-week internship project covering CSV processing, Python modules and OOP, SQLite database management, Flask dashboard development, and automated testing.
