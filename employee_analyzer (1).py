"""PS 18 - Employee Data Analyzer
Cleans employee data from a CSV file (duplicates removed, missing salaries
filled with the mean of valid salaries) and shows summary, department-wise
statistics, a salary filter and a bar chart.
CSV columns: Emp_ID, Name, Department, Salary, Experience  (dummy data only)
"""
import os
import sys

import pandas as pd

FILENAME = "employees.csv"
COLUMNS = ["Emp_ID", "Name", "Department", "Salary", "Experience"]
DEFAULT_LIMIT = 45000


def fmt(value):
    """Whole numbers without decimals, others with 2 decimals."""
    return str(int(value)) if float(value).is_integer() else f"{value:.2f}"


def load_data(path):
    """Load the CSV with Pandas and clean it. Returns a DataFrame or None."""
    if not os.path.isfile(path):
        print(f"Error: file '{path}' not found.")
        return None
    try:
        df = pd.read_csv(path, header=None, dtype=str, keep_default_na=False,
                         names=COLUMNS, skipinitialspace=True)
    except pd.errors.EmptyDataError:
        print(f"Error: file '{path}' is empty.")
        return None
    except Exception as exc:
        print(f"Error: could not read '{path}': {exc}")
        return None

    # Drop the header row if present, tidy text columns
    if len(df) and df.iloc[0]["Emp_ID"].strip().lower() == "emp_id":
        df = df.iloc[1:]
    for col in ("Emp_ID", "Name", "Department"):
        df[col] = df[col].str.strip()
    df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
    df["Experience"] = pd.to_numeric(df["Experience"], errors="coerce")
    df = df[df["Emp_ID"] != ""]

    # Remove duplicate employees (same Emp_ID), keep the first
    before = len(df)
    df = df.drop_duplicates(subset="Emp_ID", keep="first").reset_index(drop=True)
    duplicates = before - len(df)

    # Fill missing salaries with the mean of the valid salaries
    missing = int(df["Salary"].isna().sum())
    mean_salary = df["Salary"].mean()
    if df.empty or pd.isna(mean_salary):
        print("Error: no valid salary data found.")
        return None
    if missing:
        df["Salary"] = df["Salary"].fillna(mean_salary)

    if duplicates or missing:
        print(f"Duplicates removed: {duplicates}")
        print(f"Missing Salary filled with mean: {mean_salary:.2f}")
        print(f"Cleaned rows: {len(df)}")
    return df


def show_summary(df):
    top = df.loc[df["Salary"].idxmax()]
    print(f"Employees: {len(df)} | Average salary: {df['Salary'].mean():.2f}")
    print(f"Highest paid: {top['Name']} ({fmt(top['Salary'])})")
    print(f"Total payroll: {fmt(df['Salary'].sum())}")


def show_departments(df, limit):
    # groupby: employee count and average salary per department
    groups = df.groupby("Department", sort=False)["Salary"].agg(["count", "mean"])
    for dept, row in groups.iterrows():
        n = int(row["count"])
        word = "employee" if n == 1 else "employees"
        print(f"{dept}: {n} {word} | Avg salary: {row['mean']:.2f}")

    # Boolean filtering: employees above the salary limit
    above = df[df["Salary"] > limit]
    names = " | ".join(f"{r['Name']} ({fmt(r['Salary'])})" for _, r in above.iterrows())
    print(f"Above {fmt(limit)}: {names if names else 'none'}")

    plot_chart(groups)


def plot_chart(groups):
    try:
        import matplotlib
        import matplotlib.pyplot as plt
    except ImportError:
        print("(matplotlib not installed - bar chart skipped)")
        return
    plt.figure(figsize=(6, 4))
    bars = plt.bar(groups.index, groups["mean"], color="steelblue")
    for bar, v in zip(bars, groups["mean"]):
        plt.text(bar.get_x() + bar.get_width() / 2, v, f"{v:.0f}", ha="center", va="bottom")
    plt.title("Department-wise Average Salary")
    plt.xlabel("Department")
    plt.ylabel("Average Salary")
    if "agg" in matplotlib.get_backend().lower():
        plt.savefig("department_salary_chart.png")
        print("(bar chart saved to department_salary_chart.png)")
    else:
        print("(bar chart 'Department-wise Average Salary' displayed)")
        plt.show()
    plt.close()


def ask_limit():
    text = input(f"Salary limit (press Enter for {DEFAULT_LIMIT}): ").strip()
    if not text:
        return DEFAULT_LIMIT
    try:
        return float(text)
    except ValueError:
        print(f"Invalid number, using {DEFAULT_LIMIT}.")
        return DEFAULT_LIMIT


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else FILENAME
    df = load_data(path)
    if df is None:
        return
    while True:
        print("\nMenu:\n  1. Summary\n  2. Department-wise and filter above limit\n  3. Exit")
        try:
            choice = input("Enter choice: ").strip()
            if choice == "1":
                show_summary(df)
            elif choice == "2":
                show_departments(df, ask_limit())
            elif choice == "3":
                break
            else:
                print("Invalid choice. Enter 1, 2 or 3.")
        except EOFError:
            break


if __name__ == "__main__":
    main()
