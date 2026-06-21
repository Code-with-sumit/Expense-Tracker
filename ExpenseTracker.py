import json
import csv
import os
from datetime import datetime

DATA_FILE   = "expenses.json"
EXPORT_FILE = "expenses_export.csv"
BUDGET_FILE = "budget.json"

VALID_CATEGORIES = ["Food", "Travel", "Dress", "Books", "Health",
                    "Entertainment", "Rent", "Utilities", "Other"]


def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_expenses(expenses_list):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses_list, f, indent=4)


def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            return json.load(f).get("monthly_budget", 0)
    return 0


def save_budget(amount):
    with open(BUDGET_FILE, "w") as f:
        json.dump({"monthly_budget": amount}, f)


def get_valid_date(prompt):
    while True:
        date_str = input(prompt).strip()
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
            return date_str
        except ValueError:
            print("  Invalid date! Format: DD-MM-YYYY  (e.g. 21-06-2025)")


def get_valid_amount(prompt):
    while True:
        try:
            amount = float(input(prompt).strip())
            if amount <= 0:
                print("  Amount 0 se zyada hona chahiye!")
                continue
            return amount
        except ValueError:
            print("  Sirf number dalo! (e.g. 250 or 99.50)")


def get_valid_category():
    print("\n  Categories:")
    for i, cat in enumerate(VALID_CATEGORIES, 1):
        print(f"    {i}. {cat}")
    while True:
        try:
            idx = int(input("  Category number choose karo: ").strip())
            if 1 <= idx <= len(VALID_CATEGORIES):
                return VALID_CATEGORIES[idx - 1]
            print(f"  1 aur {len(VALID_CATEGORIES)} ke beech number dalo!")
        except ValueError:
            print("  Sirf number dalo!")


def get_valid_int(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val <= val <= max_val:
                return val
            print(f"  {min_val} aur {max_val} ke beech number dalo!")
        except ValueError:
            print("  Sirf number dalo!")


def check_budget_alert(expenses_list):
    budget = load_budget()
    if budget <= 0:
        return
    today = datetime.now()
    monthly = sum(
        e["amount"] for e in expenses_list
        if datetime.strptime(e["date"], "%d-%m-%Y").month == today.month
        and datetime.strptime(e["date"], "%d-%m-%Y").year == today.year
    )
    percent = (monthly / budget) * 100
    if monthly > budget:
        print(f"\n  BUDGET ALERT! Monthly budget exceed ho gaya!")
        print(f"  Budget: Rs.{budget:.2f} | Spent: Rs.{monthly:.2f} | Over by Rs.{monthly - budget:.2f}")
    elif percent >= 80:
        print(f"\n  WARNING: Monthly budget ka {percent:.0f}% use ho gaya!")
        print(f"  Budget: Rs.{budget:.2f} | Spent: Rs.{monthly:.2f} | Remaining: Rs.{budget - monthly:.2f}")


def add_expense(expenses_list):
    print("\n===== ADD EXPENSE =====")
    date        = get_valid_date("  Date (DD-MM-YYYY): ")
    category    = get_valid_category()
    description = input("  Description: ").strip() or "N/A"
    amount      = get_valid_amount("  Amount (Rs.): ")

    expense = {
        "id":          len(expenses_list) + 1,
        "date":        date,
        "category":    category,
        "description": description,
        "amount":      amount
    }
    expenses_list.append(expense)
    save_expenses(expenses_list)
    print(f"\n  Expense added! Rs.{amount:.2f} for {category} on {date}")
    check_budget_alert(expenses_list)


def view_all_expenses(expenses_list):
    print("\n===== ALL EXPENSES =====")
    if not expenses_list:
        print("  Koi expense nahi hai abhi tak!")
        return

    print(f"\n  {'#':<4} {'Date':<12} {'Category':<15} {'Description':<20} {'Amount':>10}")
    print("  " + "-" * 65)
    for i, e in enumerate(expenses_list, 1):
        print(f"  {i:<4} {e['date']:<12} {e['category']:<15} "
              f"{e['description'][:20]:<20} Rs.{e['amount']:>8.2f}")
    print("  " + "-" * 65)
    total = sum(e["amount"] for e in expenses_list)
    print(f"  {'TOTAL':<51} Rs.{total:>8.2f}")


def view_total(expenses_list):
    total = sum(e["amount"] for e in expenses_list)
    print(f"\n  Total Expenses : Rs.{total:.2f}")
    print(f"  Total Entries  : {len(expenses_list)}")


def view_summary(expenses_list):
    print("\n===== EXPENSE SUMMARY =====")
    today   = datetime.now()
    buckets = {"Daily": 0, "Weekly": 0, "Monthly": 0, "Yearly": 0}

    for e in expenses_list:
        try:
            exp_date = datetime.strptime(e["date"], "%d-%m-%Y")
        except ValueError:
            continue
        if exp_date.date() == today.date():
            buckets["Daily"] += e["amount"]
        if (exp_date.isocalendar()[1] == today.isocalendar()[1]
                and exp_date.year == today.year):
            buckets["Weekly"] += e["amount"]
        if exp_date.month == today.month and exp_date.year == today.year:
            buckets["Monthly"] += e["amount"]
        if exp_date.year == today.year:
            buckets["Yearly"] += e["amount"]

    labels = {"Daily": "Today", "Weekly": "This Week",
              "Monthly": "This Month", "Yearly": "This Year"}
    print()
    for key, label in labels.items():
        print(f"  {label:<15} : Rs.{buckets[key]:.2f}")


def delete_expense(expenses_list):
    print("\n===== DELETE EXPENSE =====")
    if not expenses_list:
        print("  Koi expense nahi hai delete karne ke liye!")
        return
    view_all_expenses(expenses_list)
    idx = get_valid_int(
        f"\n  Konsa entry delete karni hai? (1-{len(expenses_list)}, 0 = cancel): ",
        0, len(expenses_list)
    )
    if idx == 0:
        print("  Cancel. Koi change nahi hua.")
        return
    removed = expenses_list.pop(idx - 1)
    save_expenses(expenses_list)
    print(f"\n  Deleted: {removed['description']} | Rs.{removed['amount']:.2f} | {removed['date']}")


def edit_expense(expenses_list):
    print("\n===== EDIT EXPENSE =====")
    if not expenses_list:
        print("  Koi expense nahi hai edit karne ke liye!")
        return
    view_all_expenses(expenses_list)
    idx = get_valid_int(
        f"\n  Konsa entry edit karni hai? (1-{len(expenses_list)}, 0 = cancel): ",
        0, len(expenses_list)
    )
    if idx == 0:
        print("  Cancel. Koi change nahi hua.")
        return

    e = expenses_list[idx - 1]
    print(f"\n  Current: {e['date']} | {e['category']} | {e['description']} | Rs.{e['amount']:.2f}")
    print("  (Enter dabao agar same rakhna ho)\n")

    new_date = input(f"  Naya Date [{e['date']}]: ").strip()
    if new_date:
        try:
            datetime.strptime(new_date, "%d-%m-%Y")
            e["date"] = new_date
        except ValueError:
            print("  Invalid date, date nahi badla.")

    print("  Category change karni hai? (y/n): ", end="")
    if input().strip().lower() == "y":
        e["category"] = get_valid_category()

    new_desc = input(f"  Naya Description [{e['description']}]: ").strip()
    if new_desc:
        e["description"] = new_desc

    new_amt = input(f"  Naya Amount [Rs.{e['amount']:.2f}]: ").strip()
    if new_amt:
        try:
            val = float(new_amt)
            if val > 0:
                e["amount"] = val
            else:
                print("  Amount 0 se zyada hona chahiye, amount nahi badla.")
        except ValueError:
            print("  Invalid amount, amount nahi badla.")

    save_expenses(expenses_list)
    print("\n  Expense updated!")


def filter_by_category(expenses_list):
    print("\n===== FILTER BY CATEGORY =====")
    if not expenses_list:
        print("  Koi expense nahi hai!")
        return
    category = get_valid_category()
    filtered = [e for e in expenses_list if e["category"] == category]
    if not filtered:
        print(f"\n  '{category}' mein koi expense nahi mili!")
        return

    print(f"\n  {category} expenses:\n")
    print(f"  {'#':<4} {'Date':<12} {'Description':<22} {'Amount':>10}")
    print("  " + "-" * 52)
    for i, e in enumerate(filtered, 1):
        print(f"  {i:<4} {e['date']:<12} {e['description'][:22]:<22} Rs.{e['amount']:>8.2f}")
    total = sum(e["amount"] for e in filtered)
    print("  " + "-" * 52)
    print(f"  {'Total ' + category:<36} Rs.{total:>8.2f}")


def search_by_date_range(expenses_list):
    print("\n===== SEARCH BY DATE RANGE =====")
    if not expenses_list:
        print("  Koi expense nahi hai!")
        return

    start_str = get_valid_date("  Start Date (DD-MM-YYYY): ")
    end_str   = get_valid_date("  End Date   (DD-MM-YYYY): ")

    start = datetime.strptime(start_str, "%d-%m-%Y")
    end   = datetime.strptime(end_str,   "%d-%m-%Y")

    if start > end:
        print("  Start date, end date se pehle honi chahiye!")
        return

    filtered = [
        e for e in expenses_list
        if start <= datetime.strptime(e["date"], "%d-%m-%Y") <= end
    ]
    if not filtered:
        print(f"\n  {start_str} se {end_str} ke beech koi expense nahi mili!")
        return

    print(f"\n  {start_str}  to  {end_str}  ({len(filtered)} entries)\n")
    print(f"  {'#':<4} {'Date':<12} {'Category':<15} {'Description':<20} {'Amount':>10}")
    print("  " + "-" * 65)
    for i, e in enumerate(filtered, 1):
        print(f"  {i:<4} {e['date']:<12} {e['category']:<15} "
              f"{e['description'][:20]:<20} Rs.{e['amount']:>8.2f}")
    total = sum(e["amount"] for e in filtered)
    print("  " + "-" * 65)
    print(f"  {'TOTAL':<51} Rs.{total:>8.2f}")


def set_budget():
    print("\n===== SET MONTHLY BUDGET =====")
    current = load_budget()
    if current:
        print(f"  Current budget: Rs.{current:.2f}")
    budget = get_valid_amount("  Naya monthly budget set karo (Rs.): ")
    save_budget(budget)
    print(f"  Monthly budget set: Rs.{budget:.2f}")


def export_to_csv(expenses_list):
    print("\n===== EXPORT TO CSV =====")
    if not expenses_list:
        print("  Export karne ke liye koi data nahi hai!")
        return
    with open(EXPORT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "category", "description", "amount"])
        writer.writeheader()
        writer.writerows(expenses_list)
    print(f"  Exported! File: {EXPORT_FILE}")
    print(f"  Location: {os.path.abspath(EXPORT_FILE)}")


def print_menu():
    print("""
===== MENU =====
  1.  Add Expense
  2.  View All Expenses
  3.  View Total Expenses
  4.  Expense Summary
  5.  Delete Expense
  6.  Edit Expense
  7.  Filter by Category
  8.  Search by Date Range
  9.  Set Monthly Budget
  10. Export to CSV
  0.  Exit
=================""")


def main():
    expenses_list = load_expenses()

    print("\nWelcome to Expense Tracker")

    if expenses_list:
        print(f"  {len(expenses_list)} expense(s) loaded.")
        check_budget_alert(expenses_list)

    while True:
        print_menu()
        choice = input("  Enter choice (0-10): ").strip()

        if   choice == "1":  add_expense(expenses_list)
        elif choice == "2":  view_all_expenses(expenses_list)
        elif choice == "3":  view_total(expenses_list)
        elif choice == "4":  view_summary(expenses_list)
        elif choice == "5":  delete_expense(expenses_list)
        elif choice == "6":  edit_expense(expenses_list)
        elif choice == "7":  filter_by_category(expenses_list)
        elif choice == "8":  search_by_date_range(expenses_list)
        elif choice == "9":  set_budget()
        elif choice == "10": export_to_csv(expenses_list)
        elif choice == "0":
            print("\n  Thank you for using Expense Tracker! Bye!\n")
            break
        else:
            print("  Invalid choice! 0 se 10 ke beech kuch dalo.")


if __name__ == "__main__":
    main()