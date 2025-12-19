from importer import validator, importer_controller as imp
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from database.database_controller import TransactionDatabase


def load_transactions_from_db() -> pd.DataFrame:
    """
    Load transactions from database and return a DataFrame.
    """
    db = TransactionDatabase()
    transactions = db.fetch_all()

    if not transactions:
        print("Warning: No transactions found in database.")
        return pd.DataFrame()

    df = pd.DataFrame(transactions)

    df["date"] = pd.to_datetime(df["date"]).dt.date

    return df


def ensure_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


def plot_income_vs_expense(df: pd.DataFrame) -> None:
    """
    Bar chart: total income vs total expense.
    """
    summary = (
        df[df["type"].isin([imp.TransactionType.INCOME.value, imp.TransactionType.EXPENSE.value])]
        .groupby("type")["amount"]
        .sum()
        .reset_index()
    )

    sns.barplot(data=summary, x="type", y="amount")
    plt.title("Total Income vs Expense")
    plt.xlabel("Transaction Type")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.show()


def plot_expenses_by_category(df: pd.DataFrame) -> None:
    """
    Bar chart: expenses grouped by category.
    """
    expenses = df[df["type"] == validator.TransactionType.EXPENSE.value]

    category_totals = (
        expenses.groupby("category")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    sns.barplot(data=category_totals, x="amount", y="category")
    plt.title("Expenses by Category")
    plt.xlabel("Total Spent")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.show()


def plot_daily_cashflow(df: pd.DataFrame) -> None:
    """
    Line chart: daily income and expense over time.
    """
    daily = (
        df[df["type"] != imp.TransactionType.TRANSFER.value]
        .groupby(["date", "type"])["amount"]
        .sum()
        .reset_index()
    )

    sns.lineplot(
        data=daily,
        x="date",
        y="amount",
        hue="type",
        marker="o",
    )

    plt.title("Daily Cash Flow")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_expense_distribution(df: pd.DataFrame) -> None:
    """
    Pie chart: percentage distribution of expenses.
    """
    expenses = df[df["type"] == imp.TransactionType.EXPENSE.value]

    category_totals = expenses.groupby("category")["amount"].sum()

    plt.figure()
    plt.pie(
        category_totals,
        labels=category_totals.index,
        autopct="%1.1f%%",
        startangle=140,
    )
    plt.title("Expense Distribution by Category")
    plt.tight_layout()
    plt.show()


def plot_expense_outliers(df: pd.DataFrame) -> None:
    expenses = df[df["type"] == imp.TransactionType.EXPENSE.value]

    sns.boxplot(
        data=expenses,
        x="category",
        y="amount",
    )

    plt.title("Expense Outliers by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_expense_heatmap(df: pd.DataFrame) -> None:
    expenses = df[df["type"] == imp.TransactionType.EXPENSE.value]

    pivot = (
        expenses
        .groupby(["month", "category"])["amount"]
        .sum()
        .unstack(fill_value=0)
        .astype(float)
    )

    sns.heatmap(
        pivot,
        cmap="Reds",
        linewidths=0.5,
    )

    plt.title("Expense Heatmap by Category and Month")
    plt.xlabel("Category")
    plt.ylabel("Month")
    plt.tight_layout()
    plt.show()


def plot_cumulative_net_balance(df: pd.DataFrame) -> None:
    cashflow = df[df["type"] != imp.TransactionType.TRANSFER.value].copy()
    cashflow["signed_amount"] = cashflow.apply(
        lambda r: r["amount"] if r["type"] == "income" else -r["amount"],
        axis=1,
    )

    daily = (
        cashflow.groupby("date")["signed_amount"]
        .sum()
        .cumsum()
        .reset_index()
    )

    sns.lineplot(data=daily, x="date", y="signed_amount", marker="o")

    plt.title("Cumulative Net Balance Over Time")
    plt.xlabel("Date")
    plt.ylabel("Net Balance")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def main():
    df = load_transactions_from_db()

    if df.empty:
        print("No data available. Please load transactions into the database first.")
        return

    df = ensure_time_columns(df)
    while True:
        print("\n===== TRANSACTION STATISTICS =====")
        print("1) Income vs Expense")
        print("2) Expenses by Category")
        print("3) Daily Cash Flow")
        print("4) Expense Distribution")
        print("5) Expense Outliers")
        print("6) Cumulative Net Balance")
        print("7) Expense Heatmap")
        print("X) Back to main menu")

        choice = input("> ").strip()

        if choice == "1":
            plot_income_vs_expense(df)
        elif choice == "2":
            plot_expenses_by_category(df)
        elif choice == "3":
            plot_daily_cashflow(df)
        elif choice == "4":
            plot_expense_distribution(df)
        elif choice == "5":
            plot_expense_outliers(df)
        elif choice == "6":
            plot_cumulative_net_balance(df)
        elif choice == "7":
            plot_expense_heatmap(df)
        elif choice.lower() == "x":
            break
        else:
            print("Invalid choice. Please try again.")
