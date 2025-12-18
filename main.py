from database import database_main as dbm
from stats import stats as st


def main():
    """
    Main application entry point with unified menu system.
    """
    while True:
        print("\n" + "=" * 50)
        print("     TRANSACTION MANAGEMENT SYSTEM")
        print("=" * 50)
        print("1) Database Editor / Show Data")
        print("2) Statistics")
        print("X) Exit")
        print("=" * 50)

        choice = input("> ").strip().lower()

        if choice == "1":
            dbm.database_menu()

        elif choice == "2":
            st.main()

        elif choice == "x":
            print("\nGoodbye!")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
