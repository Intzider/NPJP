import csv
from pathlib import Path
from .validator import *


class TransactionImporter:
    """
    Handles CSV import and validation of financial transactions

    """

    def __init__(self, date_format: str = "%Y-%m-%d", encoding: str = "utf-8") -> None:
        """
        Initialize the transaction importer.

        :param date_format: Expected date format in CSV files
        :param encoding: File encoding (default: utf-8)
        """
        self.date_format = date_format
        self.encoding = encoding
        self.transactions: list[dict[str, Any]] = []
        self.validation_errors: list[str] = []

    def load(self, filepath: str) -> None:
        """
        Load transactions from CSV file.

        :param filepath: Path to CSV file
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        self.transactions.clear()
        self.validation_errors.clear()

        try:
            with open(path, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)

                if not reader.fieldnames:
                    raise ValueError("CSV file is empty or has no header row")

                for row_num, record in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        validated = validate_record(self.date_format, record, row_num)
                        self.transactions.append(validated)
                    except ValidationError as e:
                        self.validation_errors.append(str(e))

        except UnicodeDecodeError:
            raise ValueError(
                f"Cannot decode file with {self.encoding} encoding. "
                f"Try a different encoding."
            )

        if not self.transactions and self.validation_errors:
            raise ValueError(
                f"No valid transactions found. Errors:\n" +
                "\n".join(self.validation_errors[:5]) +
                (f"\n... and {len(self.validation_errors) - 5} more"
                 if len(self.validation_errors) > 5 else "")
            )

    def get_transactions(self) -> list[dict[str, Any]]:
        """
        Get all loaded and validated transactions.

        :return: List of transaction dictionaries
        """
        return self.transactions.copy()

    def get_validation_errors(self) -> list[str]:
        """
        Get list of validation errors encountered.

        :return: List of error messages
        """
        return self.validation_errors.copy()


class TransactionFilter:
    """
    Provides filtering capabilities for transactions

    """

    def __init__(self, transactions: list[dict[str, Any]]) -> None:
        """
        Initialize filter with transactions.

        :param transactions: List of transaction dictionaries
        """
        self.transactions = transactions

    def by_date_range(self, start_date: datetime, end_date: datetime) -> 'TransactionFilter':
        """
        Filter transactions by date range.

        :param start_date: Start date (inclusive)
        :param end_date: End date (inclusive)
        :return: Self for method chaining
        """
        self.transactions = [
            t for t in self.transactions
            if start_date <= t['date'] <= end_date
        ]
        return self

    def by_amount_range(self, min_amount: Decimal = None, max_amount: Decimal = None) -> 'TransactionFilter':
        """
        Filter transactions by amount range.

        :param min_amount: Minimum amount (inclusive)
        :param max_amount: Maximum amount (inclusive)
        :return: Self for method chaining
        """
        filtered = []
        for t in self.transactions:
            if min_amount and t['amount'] < min_amount:
                continue
            if max_amount and t['amount'] > max_amount:
                continue
            filtered.append(t)

        self.transactions = filtered
        return self

    def by_category(self, category: str) -> 'TransactionFilter':
        """
        Filter transactions by category (case-insensitive).

        :param category: Category name
        :return: Self for method chaining
        """
        cat_lower = category.lower()
        self.transactions = [
            t for t in self.transactions
            if t['category'].lower() == cat_lower
        ]
        return self

    def by_type(self, transaction_type: str) -> 'TransactionFilter':
        """
        Filter transactions by type.

        :param transaction_type: Type (income, expense, transfer)
        :return: Self for method chaining
        """
        type_normalized = transaction_type.strip().lower()
        self.transactions = [
            t for t in self.transactions
            if t['type'] == type_normalized
        ]
        return self

    def by_description(self, keyword: str) -> 'TransactionFilter':
        """
        Filter transactions by description keyword (case-insensitive).

        :param keyword: Keyword to search in description
        :return: Self for method chaining
        """
        keyword_lower = keyword.lower()
        self.transactions = [
            t for t in self.transactions
            if keyword_lower in t['description'].lower()
        ]
        return self

    def get_results(self) -> list[dict[str, Any]]:
        """
        Get current filtered transaction list.

        :return: Filtered transactions
        """
        return self.transactions.copy()
