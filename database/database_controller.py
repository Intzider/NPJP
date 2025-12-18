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
                SELECT id, date, amount, category, type, description
                FROM transactions
                ORDER BY date
            """).fetchall()

        return [
            {
                "id": r[0],
                "date": datetime.strptime(r[1], "%Y-%m-%d"),
                "amount": Decimal(str(r[2])),
                "category": r[3],
                "type": r[4],
                "description": r[5]
            }
            for r in rows
        ]

    def clear_all(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM transactions")
        conn.commit()

    def delete_by_id(self, transaction_id: int):
        """Delete a single transaction by ID"""
        with self._connect() as conn:
            cursor = conn.execute("""
                DELETE FROM transactions WHERE id = ?
            """, (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0

    def update_transaction(self, transaction_id: int, date_str: str, amount: float,
                           category: str, trans_type: str, description: str):
        """Update a transaction by ID"""
        with self._connect() as conn:
            cursor = conn.execute("""
                UPDATE transactions 
                SET date = ?, amount = ?, category = ?, type = ?, description = ?
                WHERE id = ?
            """, (date_str, amount, category, trans_type, description, transaction_id))
            conn.commit()
            return cursor.rowcount > 0

    def fetch_by_id(self, transaction_id: int):
        """Fetch a single transaction by ID"""
        with self._connect() as conn:
            row = conn.execute("""
                SELECT id, date, amount, category, type, description
                FROM transactions
                WHERE id = ?
            """, (transaction_id,)).fetchone()

        if row:
            return {
                "id": row[0],
                "date": datetime.strptime(row[1], "%Y-%m-%d"),
                "amount": Decimal(str(row[2])),
                "category": row[3],
                "type": row[4],
                "description": row[5]
            }
        return None
