from importer import TransactionImporter, TransactionFilter, TransactionType
from database import TransactionDatabase
from decimal import Decimal



# ASCII visualization helpers
def ascii_bar(label: str, value: Decimal, scale: Decimal = Decimal("10")):
    bars = int(value / scale) if value > 0 else 0
    print(f"{label:15} {'█' * bars} {value}")


def show_ascii_statistics(transactions):
    income = sum(t["amount"] for t in transactions if t["type"] == TransactionType.INCOME.value)
    expense = sum(t["amount"] for t in transactions if t["type"] == TransactionType.EXPENSE.value)
    net = income - expense

    print("\n--- STATISTICS ---")
    print(f"Total income : {income}")
    print(f"Total expense: {expense}")
    print(f"Net balance  : {net}")

    print("\n--- ASCII BAR CHART ---")
    ascii_bar("Income", income)
    ascii_bar("Expense", expense)



# Printing helpers
def print_transactions(transactions):
    print("\n--- TRANSACTIONS ---")
    for t in transactions:
        print(
            f"{t['date'].date()} | "
            f"{t['type']:7} | "
            f"{t['category']:10} | "
            f"{t['amount']:8} | "
            f"{t['description']}"
        )


def read_decimal(prompt: str):
    try:
        value=Decimal(input(prompt))
        if value<0:
            print("Amount can't be negative!")
            return None
        return value
    except:
        print("Invalid number.")
        return None



# CLI application
def main():
    db = TransactionDatabase()
    current_transactions = []

    while True:
        print("\n===== TRANSACTION TRACKER =====")
        print("1) Import CSV (validate)")
        print("2) Filter transactions")
        print("3) Show statistics (ASCII)")
        print("4) Save transactions to database")
        print("5) Load transactions from database")
        print("6) Clear database")
        print("0) Exit")

        choice = input("> ").strip()

        
        # 1. CSV IMPORT
        if choice == "1":
            path = input("CSV file path: ").strip().strip('"')
            importer = TransactionImporter()

            try:
                importer.load(path)
                current_transactions = importer.get_transactions()
                print(f"Loaded {len(current_transactions)} valid transactions.")

                if importer.get_validation_errors():
                    print("Some rows were invalid:")
                    for err in importer.get_validation_errors()[:5]:
                        print(" -", err)

            except Exception as e:
                print("Error:", e)

        
        # 2. FILTERING
        elif choice == "2":
            if not current_transactions:
                print("No transactions loaded.")
                continue

            print("Filter by:")
            print("1) Category")
            print("2) Type (income/expense)")
            print("3) Amount range")
            sub = input("> ").strip()

            tf = TransactionFilter(current_transactions)

            if sub == "1":
                cat = input("Category: ").strip()
                current_transactions = tf.by_category(cat).get_results()

            elif sub == "2":
                ttype = input("Type (income/expense): ").strip().lower()
                if ttype not in (TransactionType.INCOME.value, TransactionType.EXPENSE.value):
                    print("Invalid transaction type.")
                    continue
                current_transactions = tf.by_type(ttype).get_results()

            elif sub == "3":
                min_amt = read_decimal("Min amount: ")
                max_amt = read_decimal("Max amount: ")

                if min_amt is None or max_amt is None:
                    continue

                if min_amt > max_amt:
                    print("Minimum amount cannot be greater than maximum amount.")
                    continue

                current_transactions = tf.by_amount_range(min_amt, max_amt).get_results()

            else:
                print("Invalid filter option.")
                continue

            print(f"Remaining transactions: {len(current_transactions)}")
            print_transactions(current_transactions)

        
        # 3. ASCII STATISTICS
        elif choice == "3":
            if not current_transactions:
                print("No transactions loaded.")
                continue

            show_ascii_statistics(current_transactions)

        
        # 4. SAVE TO DATABASE
        elif choice == "4":
            if not current_transactions:
                print("No transactions to save.")
                continue

            print("Save mode:")
            print("1) Append to database")
            print("2) Overwrite database")
            mode = input("> ").strip()

            if mode == "1":
                db.insert_many(current_transactions)
                print("Transactions appended to database.")

            elif mode == "2":
                confirm = input("This will delete existing data. Continue? (yes/no): ").lower()
                if confirm == "yes":
                    db.clear_all()
                    db.insert_many(current_transactions)
                    print("Database overwritten.")
                else:
                    print("Operation cancelled.")

            else:
                print("Invalid save option.")

        
        # 5. LOAD FROM DATABASE
        elif choice == "5":
            current_transactions = db.fetch_all()
            print(f"Loaded {len(current_transactions)} transactions from database.")

        
        # 6. CLEAR DATABASE
        elif choice == "6":
            confirm = input("Delete ALL database records? (yes/no): ").lower()
            if confirm == "yes":
                db.clear_all()
                print("Database cleared.")
            else:
                print("Operation cancelled.")

        
        # EXIT
        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
