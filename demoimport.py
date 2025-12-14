from csv_manipulation.importer import (
    TransactionImporter,
    TransactionFilter,
    ValidationError
)
from datetime import datetime
from decimal import Decimal


def print_section(title: str) -> None:
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_transaction(trans: dict) -> None:
    """Pretty print a transaction"""
    print(f"  {trans['date'].date()} | {trans['type']:8} | "
          f"{trans['amount']:>10.2f} | {trans['category']:15} | {trans['description']}")


def demo_basic_import():
    """Demonstrate basic CSV import"""
    print_section("1. BASIC CSV IMPORT")

    importer = TransactionImporter()
    importer.load("example_transactions.csv")

    transactions = importer.get_transactions()
    print(f"✓ Successfully loaded {len(transactions)} transactions")
    print(f"\nFirst 5 transactions:")
    print(f"  {'Date':<12} | {'Type':<8} | {'Amount':<12} | {'Category':<15} | Description")
    print(f"  {'-' * 75}")
    for trans in transactions[:5]:
        print_transaction(trans)


def demo_statistics():
    """Demonstrate statistics generation"""
    print_section("2. TRANSACTION STATISTICS")

    importer = TransactionImporter()
    importer.load("example_transactions.csv")

    stats = importer.get_statistics()
    print(f"Total Transactions: {stats['total_transactions']}")
    print(f"Total Income:       {stats['total_income']:.2f}")
    print(f"Total Expenses:     {stats['total_expense']:.2f}")
    print(f"Net Balance:        {stats['net_balance']:.2f}")
    print(f"Date Range:         {stats['date_range'][0]} to {stats['date_range'][1]}")
    print(f"Validation Errors:  {stats['validation_errors_count']}")


def demo_callable_importer():
    """Demonstrate callable importer"""
    print_section("3. CALLABLE IMPORTER (Method Chaining)")

    importer = TransactionImporter()
    # Using importer as callable
    importer("example_transactions.csv")

    print(f"✓ Loaded {len(importer.get_transactions())} transactions using callable syntax")


def demo_filtering():
    """Demonstrate various filtering options"""
    print_section("4. TRANSACTION FILTERING")

    importer = TransactionImporter()
    importer.load("example_transactions.csv")
    transactions = importer.get_transactions()

    # Filter by date range
    print("\n--- Filter: Income transactions only ---")
    filtered = TransactionFilter(transactions).by_type("income").get_results()
    print(f"Found {len(filtered)} income transactions:")
    for trans in filtered:
        print_transaction(trans)

    # Filter by category
    print("\n--- Filter: Grocery expenses ---")
    filtered = TransactionFilter(transactions).by_category("groceries").get_results()
    print(f"Found {len(filtered)} grocery transactions:")
    for trans in filtered:
        print_transaction(trans)

    # Filter by amount range
    print("\n--- Filter: Transactions between 100 and 500 ---")
    filtered = TransactionFilter(transactions).by_amount_range(
        min_amount=Decimal('100'),
        max_amount=Decimal('500')
    ).get_results()
    print(f"Found {len(filtered)} transactions in amount range:")
    for trans in filtered[:5]:
        print_transaction(trans)
    if len(filtered) > 5:
        print(f"  ... and {len(filtered) - 5} more")


def demo_advanced_filtering():
    """Demonstrate advanced filtering"""
    print_section("5. ADVANCED FILTERING")

    importer = TransactionImporter()
    importer.load("example_transactions.csv")
    transactions = importer.get_transactions()

    # Filter by date range
    start = datetime(2024, 2, 1)
    end = datetime(2024, 2, 28)
    print(f"\n--- Filter: February transactions ---")
    filtered = TransactionFilter(transactions).by_date_range(start, end).get_results()
    print(f"Found {len(filtered)} transactions in February:")
    for trans in filtered:
        print_transaction(trans)

    # Filter by description keyword
    print("\n--- Filter: Transactions with 'salary' in description ---")
    filtered = TransactionFilter(transactions).by_description("salary").get_results()
    print(f"Found {len(filtered)} matching transactions:")
    for trans in filtered:
        print_transaction(trans)


def demo_multiple_filters():
    """Demonstrate applying multiple filters at once"""
    print_section("6. MULTIPLE FILTERS AT ONCE")

    importer = TransactionImporter()
    importer.load("example_transactions.csv")
    transactions = importer.get_transactions()

    # Apply multiple filters
    start = datetime(2024, 2, 1)
    end = datetime(2024, 3, 31)

    filtered = TransactionFilter(transactions).apply_filters(
        start_date=start,
        end_date=end,
        transaction_type="expense",
        min_amount=Decimal('100')
    )

    print(f"Filters: Feb-Mar 2024 | Expenses | Min 100")
    print(f"Found {len(filtered)} matching transactions:")
    print(f"  {'Date':<12} | {'Type':<8} | {'Amount':<12} | {'Category':<15} | Description")
    print(f"  {'-' * 75}")
    for trans in filtered:
        print_transaction(trans)


def demo_custom_filter():
    """Demonstrate custom filter predicate"""
    print_section("7. CUSTOM FILTER PREDICATE")

    importer = TransactionImporter()
    importer.load("example_transactions.csv")
    transactions = importer.get_transactions()

    # Custom predicate: expenses over 500
    filtered = TransactionFilter(transactions).by_custom(
        lambda t: t['type'] == 'expense' and t['amount'] > Decimal('500')
    ).get_results()

    print("Custom filter: Expenses > 500")
    print(f"Found {len(filtered)} matching transactions:")
    for trans in filtered:
        print_transaction(trans)


def demo_validation_errors():
    """Demonstrate validation error handling"""
    print_section("8. VALIDATION ERROR HANDLING")

    print("Creating an importer with intentionally bad data...")
    importer = TransactionImporter()
    try:
        importer.load("nonexistent_file.csv")
    except FileNotFoundError as e:
        print(f"✓ Caught FileNotFoundError: {e}")

    print("\nNote: To test validation errors, create a CSV with:")
    print("  - Missing required fields (date, amount, category, type, description)")
    print("  - Invalid date format")
    print("  - Non-numeric amounts")
    print("  - Invalid transaction types (not income/expense/transfer)")
    print("  - Empty descriptions or categories")


def demo_callable_filter():
    """Demonstrate callable filter"""
    print_section("9. CALLABLE FILTER")

    importer = TransactionImporter()
    importer.load("example_transactions.csv")
    transactions = importer.get_transactions()

    # Using filter as callable
    filter_obj = TransactionFilter(transactions)
    results = filter_obj(
        transaction_type="income",
        min_amount=Decimal('2000')
    )

    print(f"Using callable syntax: filter(transaction_type='income', min_amount=2000)")
    print(f"Found {len(results)} matching transactions:")
    for trans in results:
        print_transaction(trans)


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "FINANCIAL TRANSACTION IMPORTER" + " " * 13 + "║")
    print("║" + " " * 18 + "Import, Validate & Filter CSV" + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")

    try:
        demo_basic_import()
        demo_statistics()
        demo_callable_importer()
        demo_filtering()
        demo_advanced_filtering()
        demo_multiple_filters()
        demo_custom_filter()
        demo_callable_filter()
        demo_validation_errors()

        print_section("DEMONSTRATION COMPLETE")
        print("✓ All features demonstrated successfully!")
        print("\nKey Classes:")
        print("  • TransactionImporter  - Load and validate CSV files")
        print("  • TransactionFilter    - Filter transactions by various criteria")
        print("  • TransactionValidator - Validate individual transactions")
        print("\nFeatures:")
        print("  • CSV import with comprehensive validation")
        print("  • Multiple filtering options (date, amount, category, type, keyword)")
        print("  • Method chaining for filters")
        print("  • Callable interfaces for intuitive API")
        print("  • Detailed error handling and reporting")
        print("  • Statistics generation")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
