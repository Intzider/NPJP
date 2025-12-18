from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any

class TransactionType(Enum):
    """Enumeration for transaction types"""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


REQUIRED_FIELDS = ['date', 'amount', 'category', 'type', 'description']
VALID_TRANSACTION_TYPES = {t.value for t in TransactionType}


def validate_field_presence(record: dict[str, str], row_num: int) -> None:
    """
    Validate that all required fields are present.

    :param record: Transaction record dictionary
    :param row_num: Row number for error reporting
    """
    missing_fields = [f for f in REQUIRED_FIELDS if f not in record or not record[f].strip()]
    if missing_fields:
        raise ValidationError(
            f"Row {row_num}: Missing required fields: {', '.join(missing_fields)}"
        )


def validate_date(date_format: str, date_str: str, row_num: int) -> datetime:
    """
    Validate and parse date string.

    :param date_format: date format
    :param date_str: Date string to validate
    :param row_num: Row number for error reporting
    :return: Parsed datetime object
    """
    try:
        return datetime.strptime(date_str.strip(), date_format)
    except ValueError as e:
        raise ValidationError(
            f"Row {row_num}: Invalid date format '{date_str}'. Expected: {date_format}"
        )


def validate_amount(amount_str: str, row_num: int = None) -> Decimal:
    """
    Validate and parse amount value.

    :param amount_str: Amount string to validate
    :param row_num: Row number for error reporting
    :return: Decimal representation of amount
    """

    row = "" if row_num is None else f"Row {row_num}: "
    try:
        amount = Decimal(amount_str.strip())
        if amount < 0:
            raise ValidationError(f"{row}Amount cannot be negative: {amount}")
        if amount == 0:
            raise ValidationError(f"{row}Amount cannot be zero")
        return amount
    except InvalidOperation:
        raise ValidationError(f"{row}Invalid amount format '{amount_str}'. Must be a valid number.")


def validate_transaction_type(trans_type: str, row_num: int) -> str:
    """
    Validate transaction type.

    :param trans_type: Transaction type string
    :param row_num: Row number for error reporting
    :return: Normalized transaction type
    """
    normalized = trans_type.strip().lower()
    if normalized not in VALID_TRANSACTION_TYPES:
        raise ValidationError(
            f"Row {row_num}: Invalid transaction type '{trans_type}'. "
            f"Must be one of: {', '.join(VALID_TRANSACTION_TYPES)}"
        )
    return normalized


def validate_category(category: str, row_num: int) -> str:
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


def validate_description(description: str, row_num: int) -> str:
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


def validate_record(date_format: str, record: dict[str, str], row_num: int) -> dict[str, Any]:
    """
    Validate complete transaction record.

    :param date_format: date format
    :param record: Transaction record dictionary
    :param row_num: Row number for error reporting
    :return: Validated and normalized record dictionary
    """
    validate_field_presence(record, row_num)

    return {
        'date': validate_date(date_format, record['date'], row_num),
        'amount': validate_amount(record['amount'], row_num),
        'category': validate_category(record['category'], row_num),
        'type': validate_transaction_type(record['type'], row_num),
        'description': validate_description(record['description'], row_num),
        'original_record': record
    }
