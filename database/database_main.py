from importer import validator, importer_controller as imp
from importer.validator import ValidationError, validate_amount
from .database_controller import TransactionDatabase
from datetime import datetime


def print_transactions(transactions):
    print("\n--- TRANSACTIONS ---")

    transactions = sorted(transactions, key=lambda tr: tr['id'])

    for t in transactions:
        print(
            f"{t['id']:<5} | "
            f"{t['date'].date()} | "
            f"{t['type']:8} | "
            f"{t['category']:13} | "
            f"{t['amount']:8} | "
            f"{t['description']}"
        )


def read_decimal(amount: str):
    try:
        return validate_amount(amount)
    except ValidationError:
        print("Invalid number, leaving blank")
        return None


# CLI application
def database_menu():
    db = TransactionDatabase()
    current_transactions = []

    while True:
        print("\n===== DATABASE EDITOR =====")
        print("1) Import CSV (validate)")
        print("2) Save transactions to database")
        print("3) Load all transactions from database")
        print("4) Load with filters")
        print("5) Edit transaction by ID")
        print("6) Delete transaction by ID")
        print("7) Clear database")
        print("X) Back to main menu")

        choice = input("> ").strip()

        # 1. CSV IMPORT
        if choice == "1":
            path = input("CSV file path: ").strip().strip('"')
            importer = imp.TransactionImporter()

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

        # 2. SAVE TO DATABASE
        elif choice == "2":
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


        # 3. LOAD FROM DATABASE
        elif choice == "3":
            current_transactions = db.fetch_all()
            print(f"Loaded {len(current_transactions)} transactions from database.")
            print_transactions(current_transactions)


        # 4. LOAD WITH FILTERS
        elif choice == "4":
            all_transactions = db.fetch_all()
            if not all_transactions:
                print("No transactions in database.")
                continue

            transaction_filter = imp.TransactionFilter(all_transactions)

            print("\n--- Filter Options ---")
            print("Leave blank to skip a filter")

            trans_type = input("Transaction type (income/expense/transfer): ").strip()
            if trans_type:
                transaction_filter.by_type(trans_type)

            category = input("Category: ").strip()
            if category:
                transaction_filter.by_category(category)

            min_amt = read_decimal(input("Minimum amount: ").strip())
            max_amt = read_decimal(input("Maximum amount: ").strip())

            if min_amt or max_amt:
                transaction_filter.by_amount_range(min_amt, max_amt)

            desc_keyword = input("Description keyword: ").strip()
            if desc_keyword:
                transaction_filter.by_description(desc_keyword)

            current_transactions = transaction_filter.get_results()
            print(f"\nFound {len(current_transactions)} matching transactions.")
            print_transactions(current_transactions)

        # 5. EDIT TRANSACTION
        elif choice == "5":
            try:
                trans_id = int(input("Enter transaction ID to edit: ").strip())
                transaction = db.fetch_by_id(trans_id)

                if not transaction:
                    print("Transaction not found.")
                    continue

                print("\nCurrent transaction:")
                print_transactions([transaction])

                print("\nEnter new values (press Enter to keep current value):")

                date_str = input(f"Date ({transaction['date'].date()}): ").strip()
                if not date_str:
                    date_str = transaction['date'].strftime("%Y-%m-%d")
                else:
                    try:
                        datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        print("Invalid date format. Keeping original.")
                        date_str = transaction['date'].strftime("%Y-%m-%d")

                amount_input = input(f"Amount ({transaction['amount']}): ").strip()
                if amount_input:
                    try:
                        amount = read_decimal(amount_input)
                    except ValidationError:
                        print("Invalid amount. Keeping original.")
                        amount = transaction['amount']
                else:
                    amount = transaction['amount']

                category = input(f"Category ({transaction['category']}): ").strip()
                if not category:
                    category = transaction['category']

                trans_type = input(f"Type ({transaction['type']}): ").strip()
                if not trans_type:
                    trans_type = transaction['type']

                description = input(f"Description ({transaction['description']}): ").strip()
                if not description:
                    description = transaction['description']

                if db.update_transaction(trans_id, date_str, float(amount), category, trans_type, description):
                    print("Transaction updated successfully.")
                else:
                    print("Failed to update transaction.")

            except ValueError:
                print("Invalid ID format.")
            except Exception as e:
                print(f"Error: {e}")

        # 6. DELETE TRANSACTION
        elif choice == "6":
            try:
                trans_id = int(input("Enter transaction ID to delete: ").strip())
                transaction = db.fetch_by_id(trans_id)

                if not transaction:
                    print("Transaction not found.")
                    continue

                print("\nTransaction to delete:")
                print_transactions([transaction])

                confirm = input("Are you sure you want to delete this transaction? (yes/no): ").lower()
                if confirm == "yes":
                    if db.delete_by_id(trans_id):
                        print("Transaction deleted successfully.")
                    else:
                        print("Failed to delete transaction.")
                else:
                    print("Operation cancelled.")

            except ValueError:
                print("Invalid ID format.")
            except Exception as e:
                print(f"Error: {e}")

        # 7. CLEAR DATABASE
        elif choice == "7":
            confirm = input("Delete ALL database records? (yes/no): ").lower()
            if confirm == "yes":
                db.clear_all()
                print("Database cleared.")
            else:
                print("Operation cancelled.")


        # EXIT
        elif choice.lower() == "x":
            break

        else:
            print("Invalid option.")
