import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from pathlib import Path
from typing import Callable, Any


class TransactionType(Enum):
    """Enumeration for transaction types"""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class TransactionValidator:
    """
    Validates individual transaction records

    """

    REQUIRED_FIELDS = ['date', 'amount', 'category', 'type', 'description']
    VALID_TRANSACTION_TYPES = {t.value for t in TransactionType}

    def __init__(self, date_format: str = "%Y-%m-%d") -> None:
        """
        Initialize validator with specified date format.

        :param date_format: Expected date format (default: YYYY-MM-DD)
        """
        self.date_format = date_format

    def validate_field_presence(self, record: dict[str, str], row_num: int) -> None:
        """
        Validate that all required fields are present.

        :param record: Transaction record dictionary
        :param row_num: Row number for error reporting
        """
        missing_fields = [f for f in self.REQUIRED_FIELDS if f not in record or not record[f].strip()]
        if missing_fields:
            raise ValidationError(
                f"Row {row_num}: Missing required fields: {', '.join(missing_fields)}"
            )

    def validate_date(self, date_str: str, row_num: int) -> datetime:
        """
        Validate and parse date string.

        :param date_str: Date string to validate
        :param row_num: Row number for error reporting
        :return: Parsed datetime object
        """
        try:
            return datetime.strptime(date_str.strip(), self.date_format)
        except ValueError as e:
            raise ValidationError(
                f"Row {row_num}: Invalid date format '{date_str}'. Expected: {self.date_format}"
            )

    def validate_amount(self, amount_str: str, row_num: int) -> Decimal:
        """
        Validate and parse amount value.

        :param amount_str: Amount string to validate
        :param row_num: Row number for error reporting
        :return: Decimal representation of amount
        """
        try:
            amount = Decimal(amount_str.strip())
            if amount < 0:
                raise ValidationError(f"Row {row_num}: Amount cannot be negative: {amount}")
            if amount == 0:
                raise ValidationError(f"Row {row_num}: Amount cannot be zero")
            return amount
        except InvalidOperation:
            raise ValidationError(f"Row {row_num}: Invalid amount format '{amount_str}'. Must be a valid number.")

    def validate_transaction_type(self, trans_type: str, row_num: int) -> str:
        """
        Validate transaction type.

        :param trans_type: Transaction type string
        :param row_num: Row number for error reporting
        :return: Normalized transaction type
        """
        normalized = trans_type.strip().lower()
        if normalized not in self.VALID_TRANSACTION_TYPES:
            raise ValidationError(
                f"Row {row_num}: Invalid transaction type '{trans_type}'. "
                f"Must be one of: {', '.join(self.VALID_TRANSACTION_TYPES)}"
            )
        return normalized

    def validate_category(self, category: str, row_num: int) -> str:
        """
        Validate category field (non-empty string).

        :param category: Category string
        :param row_num: Row number for error reporting
        :return: Stripped and normalized category
        """
        normalized = category.strip()
        if not normalized or len(normalized) < 2:
            raise ValidationError(
                f"Row {row_num}: Category must be at least 2 characters long"
            )
        return normalized

    def validate_description(self, description: str, row_num: int) -> str:
        """
        Validate description field (non-empty string).

        :param description: Description string
        :param row_num: Row number for error reporting
        :return: Stripped description
        """
        normalized = description.strip()
        if not normalized:
            raise ValidationError(f"Row {row_num}: Description cannot be empty")
        return normalized

    def validate_record(self, record: dict[str, str], row_num: int) -> dict[str, Any]:
        """
        Validate complete transaction record.

        :param record: Transaction record dictionary
        :param row_num: Row number for error reporting
        :return: Validated and normalized record dictionary
        """
        self.validate_field_presence(record, row_num)

        return {
            'date': self.validate_date(record['date'], row_num),
            'amount': self.validate_amount(record['amount'], row_num),
            'category': self.validate_category(record['category'], row_num),
            'type': self.validate_transaction_type(record['type'], row_num),
            'description': self.validate_description(record['description'], row_num),
            'original_record': record  # Keep original for reference
        }


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
        self.validator = TransactionValidator(date_format)
        self.encoding = encoding
        self.transactions: list[dict[str, Any]] = []
        self.validation_errors: list[str] = []

    def __call__(self, filepath: str) -> 'TransactionImporter':
        """
        Make the importer callable - load transactions from CSV.

        :param filepath: Path to CSV file
        :return: Self for method chaining
        """
        self.load(filepath)
        return self

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
                        validated = self.validator.validate_record(record, row_num)
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

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about loaded transactions.

        :return: Dictionary with transaction statistics
        """
        if not self.transactions:
            return {
                'total_transactions': 0,
                'total_income': Decimal('0'),
                'total_expense': Decimal('0'),
                'net_balance': Decimal('0'),
                'date_range': None,
                'validation_errors_count': len(self.validation_errors)
            }

        income = sum(
            t['amount'] for t in self.transactions
            if t['type'] == TransactionType.INCOME.value
        )
        expense = sum(
            t['amount'] for t in self.transactions
            if t['type'] == TransactionType.EXPENSE.value
        )

        dates = [t['date'] for t in self.transactions]

        return {
            'total_transactions': len(self.transactions),
            'total_income': income,
            'total_expense': expense,
            'net_balance': income - expense,
            'date_range': (min(dates).date(), max(dates).date()) if dates else None,
            'validation_errors_count': len(self.validation_errors)
        }


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

    def __call__(self, **kwargs) -> list[dict[str, Any]]:
        """
        Make filter callable with filtering criteria.

        :param kwargs: Filtering criteria
        :return: Filtered list of transactions
        """
        return self.apply_filters(**kwargs)

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

    def by_categories(self, categories: list[str]) -> 'TransactionFilter':
        """
        Filter transactions by multiple categories.

        :param categories: List of category names
        :return: Self for method chaining
        """
        cats_lower = {c.lower() for c in categories}
        self.transactions = [
            t for t in self.transactions
            if t['category'].lower() in cats_lower
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

    def by_custom(self, predicate: Callable[[dict[str, Any]], bool]) -> 'TransactionFilter':
        """
        Filter transactions by custom predicate function.

        :param predicate: Function that returns True for transactions to keep
        :return: Self for method chaining
        """
        self.transactions = [t for t in self.transactions if predicate(t)]
        return self

    def apply_filters(self,
                      start_date: datetime = None,
                      end_date: datetime = None,
                      min_amount: Decimal = None,
                      max_amount: Decimal = None,
                      category: str = None,
                      categories: list[str] = None,
                      transaction_type: str = None,
                      description_keyword: str = None) -> list[dict[str, Any]]:
        """
        Apply multiple filters at once.

        Args:
            start_date: Start date for date range
            end_date: End date for date range
            min_amount: Minimum transaction amount
            max_amount: Maximum transaction amount
            category: Single category to filter
            categories: Multiple categories to filter
            transaction_type: Transaction type to filter
            description_keyword: Keyword in description

        Returns:
            Filtered list of transactions
        """
        filtered = self.transactions.copy()

        if start_date and end_date:
            filtered = [
                t for t in filtered
                if start_date <= t['date'] <= end_date
            ]

        if min_amount is not None:
            filtered = [t for t in filtered if t['amount'] >= min_amount]

        if max_amount is not None:
            filtered = [t for t in filtered if t['amount'] <= max_amount]

        if category:
            cat_lower = category.lower()
            filtered = [
                t for t in filtered
                if t['category'].lower() == cat_lower
            ]

        if categories:
            cats_lower = {c.lower() for c in categories}
            filtered = [
                t for t in filtered
                if t['category'].lower() in cats_lower
            ]

        if transaction_type:
            type_normalized = transaction_type.strip().lower()
            filtered = [t for t in filtered if t['type'] == type_normalized]

        if description_keyword:
            keyword_lower = description_keyword.lower()
            filtered = [
                t for t in filtered
                if keyword_lower in t['description'].lower()
            ]

        return filtered

    def get_results(self) -> list[dict[str, Any]]:
        """
        Get current filtered transaction list.

        :return: Filtered transactions
        """
        return self.transactions.copy()

    def reset(self, transactions: list[dict[str, Any]]) -> 'TransactionFilter':
        """
        Reset filter to original transaction list.

        :param transactions: Original transaction list
        :return: Self for method chaining
        """
        self.transactions = transactions.copy()
        return self
