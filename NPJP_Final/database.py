import sqlite3
from pathlib import Path
from datetime import datetime
from decimal import Decimal

DB_PATH = Path("transactions.db")


class TransactionDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    amount REAL,
                    category TEXT,
                    type TEXT,
                    description TEXT
                )
            """)
            conn.commit()

    def insert_many(self, transactions):
        with self._connect() as conn:
            conn.executemany("""
                INSERT INTO transactions (date, amount, category, type, description)
                VALUES (?, ?, ?, ?, ?)
            """, [
                (
                    t["date"].strftime("%Y-%m-%d"),
                    float(t["amount"]),
                    t["category"],
                    t["type"],
                    t["description"]
                )
                for t in transactions
            ])
            conn.commit()

    def fetch_all(self):
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT date, amount, category, type, description
                FROM transactions
                ORDER BY date
            """).fetchall()

        return [
            {
                "date": datetime.strptime(r[0], "%Y-%m-%d"),
                "amount": Decimal(str(r[1])),
                "category": r[2],
                "type": r[3],
                "description": r[4]
            }
            for r in rows
        ]

    def clear_all(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM transactions")
        conn.commit()
