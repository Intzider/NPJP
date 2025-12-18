import importer as imp
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def load_transactions(csv_path: str) -> pd.DataFrame:
    """
    Load transactions using TransactionImporter and return a DataFrame.
    """
    importer = imp.TransactionImporter()
    importer.load(csv_path)

    transactions = importer.get_transactions()

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
    expenses = df[df["type"] == imp.TransactionType.EXPENSE.value]

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

def plot_category_share_over_time(df: pd.DataFrame) -> None:
    expenses = df[df["type"] == imp.TransactionType.EXPENSE.value]

    monthly = (
        expenses
        .groupby(["month", "category"])["amount"]
        .sum()
        .reset_index()
    )

    pivot = monthly.pivot(
        index="month",
        columns="category",
        values="amount",
    ).fillna(0).astype(float)

    pivot.plot(kind="area", stacked=True, figsize=(10, 6))

    plt.title("Expense Category Share Over Time")
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.xticks(rotation=45)
    plt.legend(title="Category", bbox_to_anchor=(1.05, 1))
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


def plot_monthly_cashflow_rolling(df: pd.DataFrame) -> None:
    df_filtered = df[df["type"] != imp.TransactionType.TRANSFER.value].copy()

    df_grouped = (
        df_filtered.groupby([df_filtered["date"].dt.to_period("M"), "type"])["amount"]
        .sum()
        .reset_index()
    )

    df_grouped["month"] = df_grouped["date"].astype(str)

    pivot = df_grouped.pivot(index="month", columns="type", values="amount").fillna(0)
    pivot = pivot.astype(float)

    rolling = pivot.rolling(3, min_periods=1).mean()

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=pivot, markers=True, dashes=False)
    sns.lineplot(data=rolling, linestyle="--")
    plt.title("Monthly Income and Expenses with 3-Month Rolling Average")
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.xticks(rotation=45)
    plt.legend(title="Type / Rolling")
    plt.tight_layout()
    plt.show()

def plot_category_correlation(df: pd.DataFrame) -> None:
    expenses = df[df["type"] == imp.TransactionType.EXPENSE.value].copy()

    pivot = (
        expenses.groupby([expenses["date"].dt.to_period("M"), "category"])["amount"]
        .sum()
        .unstack(fill_value=0)
        .astype(float)
    )

    corr = pivot.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
    )
    plt.title("Correlation Between Expense Categories")
    plt.tight_layout()
    plt.show()

def main():
    csv_path = "transactions.csv"

    df = load_transactions(csv_path)
    df = ensure_time_columns(df)
    while True:
        print("\n===== TRANSACTION STATISTICS =====")
        print("1) Income vs Expense")
        print("2) Expenses by Category")
        print("3) Daily Cash Flow")
        print("4) Expense Distribution")
        print("5) Expense Outliers")
        print("6) Category Share Over Time")
        print("7) Cumulative Net Balance")
        print("8) Monthly Cash Flow with Rolling Average")
        print("9) Category Correlation")
        print("0) Expense Heatmap")
        print("X) Exit")

        choice = input("> ").strip()

        if choice == "0":
            plot_expense_heatmap(df)
        elif choice == "1":
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
            plot_category_share_over_time(df)
        elif choice == "7":
            plot_cumulative_net_balance(df)
        elif choice == "8":
            plot_monthly_cashflow_rolling(df)
        elif choice == "9":
            plot_category_correlation(df)
        elif choice.lower() == "x":
            break
        else:
            print("Invalid choice. Please try again.")