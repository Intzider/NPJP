import importer as imp
import stats as st
import database as db
import dbImplementation as dbi
from datetime import datetime
from decimal import Decimal


importer = imp.TransactionImporter()
importer.load("transactions.csv")

transactions = importer.get_transactions()

print(f"Loaded {len(transactions)} valid transactions")
print(f"Validation errors: {len(importer.get_validation_errors())}")
print("-" * 60)


groceries_expenses = (
    imp.TransactionFilter(transactions)
        .by_type("expense")
        .by_category("Groceries")
        .by_amount_range(min_amount=Decimal("20"))
        .by_description("market")
        .get_results()
    )

print(f"Filtered grocery expenses: {len(groceries_expenses)}")
for t in groceries_expenses[:5]:
    print(t["date"].date(), t["category"], t["amount"], t["description"])

print("-" * 60)

filtered_expenses = imp.TransactionFilter(transactions)(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    min_amount=Decimal("50"),
    transaction_type="expense"
    )

print(f"Expenses >= 50 in 2024: {len(filtered_expenses)}")

tf = imp.TransactionFilter(transactions)

groceries = tf.by_category("Groceries").get_results()
print(f"Total grocery transactions: {len(groceries)}")

tf.reset(transactions)

income = tf.by_type("income").get_results()
print(f"Total income transactions: {len(income)}")

print("-" * 60)

march_food_expenses = (
    imp.TransactionFilter(transactions)
        .by_date_range(
            datetime(2024, 3, 1),
            datetime(2024, 3, 31)
        )
        .by_categories(["Groceries", "Restaurants"])
        .by_type("expense")
        .get_results()
    )

total_spent = sum(t["amount"] for t in march_food_expenses)
print(f"Total food spending in March 2024: {total_spent}")

print("-" * 60)

st.main()
dbi.main()