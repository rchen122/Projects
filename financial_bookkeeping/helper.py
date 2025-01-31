import csv
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # Requires `pip install python-dateutil`


def get_time():
    with open("current_time.txt", "r") as file:
        date_str = file.read().strip()
        dt = datetime.strptime(date_str, "%m-%d-%Y")
        formatted_date = dt.strftime("%m-%d-%Y")
        return formatted_date
    
def advance_time():
    with open("current_time.txt", "r") as file:
        date_str = file.read().strip()

    date_obj = datetime.strptime(date_str, "%m-%d-%Y")
    new_date = date_obj + relativedelta(months=1)

    with open("current_time.txt", "w") as file:
        file.write(new_date.strftime("%m-%d-%Y"))

def view_list(group):
    group_list = []
    with open(f'{group}.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            group_list.append(row)
    return group_list

def add(group, data):
    with open(f"{group}.csv", 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writerow(data)

def load_income_statement():
    with open("income_statement.json", "r") as file:
        data = json.load(file)

    revenue = data["Revenue"]
    expenses = data["Expenses"]

    total_revenue = revenue["Sales"] - revenue["COGS"]
    total_expenses = sum(expenses.values())
    net_income = total_revenue - total_expenses

    return revenue, expenses, total_revenue, total_expenses, net_income

def load_balance_sheet():
    with open("balance.json", "r") as file:
        data = json.load(file)

    assets = data["Assets"]
    liabilities = data["Liabilities"]

    total_current_assets = sum(assets["Current Assets"].values())
    total_fixed_assets = sum(assets["Fixed Assets"].values())
    total_assets = total_current_assets + total_fixed_assets

    total_current_liabilities = sum(liabilities["Current Liabilities"].values())
    total_long_term_liabilities = sum(liabilities["Long Term Liabilities"].values())
    total_liabilities = total_current_liabilities + total_long_term_liabilities

    net_worth = total_assets - total_liabilities

    return (
        assets, liabilities, total_current_assets, total_fixed_assets, total_assets,
        total_current_liabilities, total_long_term_liabilities, total_liabilities, net_worth
    )

def load_history(name):
    with open(f"{name}.json", "r") as file:
        history = json.load(file)
    
    # Sort by date (most recent first)
    history.sort(key=lambda x: x["date"], reverse=True)
    
    return history

def get_employee_names():
    employee_names = []
    
    with open("employees.csv", mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            full_name = f"{row['First Name']} {row['Last Name']}"
            employee_names.append(full_name)
    
    return employee_names

def get_customer_names():
    customers = []
    
    with open("customers.csv", mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            customers.append(row["Company Name"])

    return customers

def get_part_names():
    parts = []
    with open("vendors.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            parts.append(row["Part"])
    return parts

def get_salary(employee):
    first_name, last_name = employee.split()
    with open("employees.csv", mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["First Name"] == first_name and row["Last Name"] == last_name:
                return row["Salary"]  
    return None  # Return None if employee is not found

def calculate_withholding(salary):
    federal_income_t = 0.19
    SS_t = 0.062
    medicare_t = 0.0145
    state_t = 0.0495

    fed_withhold = salary * federal_income_t
    SS_withhold = salary * SS_t
    medicare_withhold = salary * medicare_t
    state_withhold = salary * state_t

    amount_paid = salary - fed_withhold - SS_withhold - medicare_withhold - state_withhold
    return fed_withhold, state_withhold, SS_withhold, medicare_withhold, amount_paid

def get_inventory():
    inventory = {}
    inventory_list = []
    with open("inventory.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            part = row["Part"].strip()
            price_per_unit = float(row["Price/Unit"].strip())
            quantity = int(row["Quantity"].strip())
            value = price_per_unit * quantity
            inventory[part] = quantity
            inventory_list.append({
                "Part": part,
                "Price/Unit": price_per_unit,
                "Quantity": quantity,
                "Value": value
            })

    bom = []
    with open("bom.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            item = row["Item"].strip()
            quantity_per_unit = int(row["Quantity/Truck"].strip())
            bom.append((item, quantity_per_unit))


    max_units = float("inf")  # Start with a very large number
    for item, qty_needed in bom:
        available_qty = inventory.get(item, 0)  # Default to 0 if part is missing
        if qty_needed > 0:
            max_units = min(max_units, available_qty // qty_needed)

    max_units = max_units if max_units != float("inf") else 0

    return inventory_list, max_units

def get_price(customer_name):
    with open("customers.csv", 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row["Company Name"] == customer_name:
                return row["Price"]
    return None

def get_cost(part):
    with open("vendors.csv", 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row["Part"] == part:
                return row['Price/Unit']
    return None

def update_inventory_value():
    total_value = 0

    with open('inventory.csv', "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            price_per_unit = float(row["Price/Unit"])
            quantity = int(row["Quantity"])
            total_value += price_per_unit * quantity  # Calculate value and add to total

    with open("balance.json", 'r') as file:
        balance = json.load(file)
    
    balance["Assets"]["Current Assets"]["Inventory"] = total_value
    with open("balance.json", 'w') as file:
        json.dump(balance, file, indent=4)

def update_inventory(amount):
    # Load BOM data
    bom = {}
    with open("bom.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            item = row["Item"].strip()
            quantity_per_unit = int(row["Quantity/Truck"].strip())
            bom[item] = quantity_per_unit * amount  # Total required amount

    # Load Inventory data
    inventory = []
    with open("inventory.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        fieldnames = csv_reader.fieldnames  # Keep headers for writing back
        for row in csv_reader:
            part = row["Part"].strip()
            quantity = int(row["Quantity"].strip())

            # Subtract required quantity if part exists in BOM
            if part in bom:
                row["Quantity"] = max(0, quantity - bom[part])  # Ensure non-negative quantity
            
            inventory.append(row)

    # Write updated inventory back to CSV
    with open("inventory.csv", "w", newline="") as file:
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(inventory)
    update_inventory_value()
    
def add_PO_inventory(part_name, amount):
    inventory = []

    # Read inventory and update the specified part
    with open("inventory.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        fieldnames = csv_reader.fieldnames  # Keep headers for writing back
        for row in csv_reader:
            part = row["Part"].strip()
            quantity = int(row["Quantity"].strip())

            # Add the specified amount to the matching part
            if part == part_name:
                row["Quantity"] = quantity + amount
            
            inventory.append(row)

    # Write updated inventory back to CSV
    with open("inventory.csv", "w", newline="") as file:
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(inventory)
    update_inventory_value()


