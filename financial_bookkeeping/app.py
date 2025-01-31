from flask import Flask, render_template, request, redirect
from helper import *

app = Flask(__name__)


@app.route('/')
def home():
    time = get_time()
    return render_template('index.html', time=time)

@app.route('/employee', methods=['POST'])
def employee():
    button_value = request.form['button']
    if button_value == "View Employees":
        employees = view_list("employees")
        return render_template('employee.html', employees=employees)
    elif button_value == "Add Employees":
        return render_template("add_employee.html")
    elif button_value == "Pay an Employee":
        employee_list = get_employee_names()
        return render_template("pay_employee.html", employees=employee_list)
    elif button_value == "View Payroll Events":
        payroll = load_history("payroll")
        return render_template("payroll.html", payroll_history=payroll)

    return render_template("index.html")


@app.route('/customer', methods=['POST'])
def customer():
    button_value = request.form['button']
    if button_value == "View Customers":
        customers = view_list("customers")
        return render_template('customer.html', customers=customers)
    elif button_value == "Add Customers":
        return render_template("add_customer.html")
    elif button_value == "Create Invoice":
        customers = get_customer_names()
        _, units = get_inventory()
        return render_template('invoice.html', customers=customers,units=units)
    elif button_value == "Invoice History":
        invoice = load_history("invoice")
        return render_template('invoice_history.html',history=invoice)



@app.route('/logistics', methods=["POST"])
def logistics():
    button_value = request.form['button']
    if button_value == "View Vendors":
        vendors = view_list("vendors")
        return render_template('vendor.html', vendors=vendors)
    elif button_value == "Add Vendors":
        return render_template("add_vendor.html")
    elif button_value == "Create PO":
        parts = get_part_names()
        return render_template("purchase_order.html", parts=parts)
    elif button_value == "View Inventory":
        inventory_items, units = get_inventory()
        return render_template("inventory.html", inventory=inventory_items, units=units)
    elif button_value == "View PO History":
        PO = load_history("purchase_order")
        return render_template("po_history.html", history=PO)

@app.route('/finance', methods=["POST"])
def view_finance():
    button_value = request.form['button']
    if button_value == "View the P&L": # display Income Statement
        revenue, expenses, total_revenue, total_expenses, net_income = load_income_statement()
        return render_template("income_statement.html", 
                           revenue=revenue, 
                           expenses=expenses, 
                           total_revenue=total_revenue, 
                           total_expenses=total_expenses, 
                           net_income=net_income)
    elif button_value == "View the Balance":
        (assets, liabilities, total_current_assets, total_fixed_assets, total_assets,
        total_current_liabilities, total_long_term_liabilities, total_liabilities, net_worth) = load_balance_sheet()
        return render_template("balance.html", 
                        assets=assets, liabilities=liabilities,
                        total_current_assets=total_current_assets, 
                        total_fixed_assets=total_fixed_assets, 
                        total_assets=total_assets,
                        total_current_liabilities=total_current_liabilities, 
                        total_long_term_liabilities=total_long_term_liabilities, 
                        total_liabilities=total_liabilities,
                        net_worth=net_worth)


@app.route("/submit_employee", methods=["POST"])
def submit_employee():
    employee_data = {
        'Last Name': request.form['last_name'],
        'First Name': request.form['first_name'],
        'Address Line 1': request.form['address1'],
        'Address Line 2': request.form['address2'],
        'City': request.form['city'],
        'State': request.form['state'],
        'Zip': request.form['zip'],
        'SSN#': request.form['ssn'],
        'Number of Withholdings': request.form['withholdings'],
        'Salary': request.form['salary']}
    add("employees", employee_data)
    return redirect('/')

@app.route("/submit_customer", methods=["POST"])
def submit_customer():
    customer_data = {
        'Company Name': request.form['company_name'],
        'Last Name': request.form['last_name'],
        'First Name': request.form['first_name'],
        'Address Line 1': request.form['address1'],
        'Address Line 2': request.form['address2'],
        'City': request.form['city'],
        'State': request.form['state'],
        'Zip': request.form['zip']
        }
    add("customers", customer_data)
    return redirect('/')

@app.route("/submit_vendor", methods=["POST"])
def submit_vendor():
    vendor_data = {
        'Company Name': request.form['vendor_name'],
        'Part': request.form['part'],
        'Price/Unit': request.form['price'],
        'Address 1': request.form['address1'],
        'Address 2': request.form['address2'],
        'City': request.form['city'],
        'State': request.form['state'],
        'Zip': request.form['zip']
        }
    add("vendors", vendor_data)
    return redirect('/')

@app.route("/pay_employee", methods=["POST"])
def process_employee_payment():
    selected_employee = request.form.get('employee')
    #determine salary amount
    salary = float(get_salary(selected_employee))
    #deduct cash from balance sheet
    with open("balance.json", "r") as file:
        balance_data = json.load(file)
        balance_data["Assets"]["Current Assets"]["Cash"] -= salary

    with open("balance.json", "w") as file:
        json.dump(balance_data, file, indent=4)
    #add salary amount to payroll and payroll withholding on income statement expense
    fed_withhold, state_withhold, SS_withhold, medicare_withhold, amount_paid = calculate_withholding(salary)
    total_withhold = fed_withhold + state_withhold + SS_withhold + medicare_withhold
    with open("income_statement.json", "r") as file:
        income_statement = json.load(file)
        income_statement["Expenses"]["Payroll"] += amount_paid
        income_statement["Expenses"]["Payroll Withholding"] += total_withhold
    with open("income_statement.json", "w") as file:
        json.dump(income_statement, file, indent=4)

    #add to payroll history
    with open("payroll.json", "r") as file:
        payroll_history = json.load(file)
    
    cur_entry = {
        "date": get_time(),
        "employee": selected_employee,
        "salary": salary,
        "federal_tax": fed_withhold,
        "state_tax": state_withhold,
        "ss_tax": SS_withhold,
        "medicare_tax": medicare_withhold,
        "amount_paid": amount_paid
    }
    payroll_history.append(cur_entry)
    with open("payroll.json", "w") as file:
        json.dump(payroll_history, file, indent=4)

    return redirect('/')

@app.route('/process_invoice', methods=["POST"])
def process_invoice():
    COGS = 0.57
    customer = request.form.get("customer")
    amount = int(request.form.get("amount"))
    inventory, units = get_inventory()
    customer_price = float(get_price(customer))
    cost = round(COGS * amount, 2)

    if amount > units:
        return "Not enough Units!"
    sale = customer_price * amount
    receivable_amount = round(sale * 0.34, 2)
    cash_amount = round(sale * 0.66, 2)
    #update balance sheet
    with open("balance.json", "r") as file:
        balance_data = json.load(file)
        balance_data["Assets"]["Current Assets"]["Cash"] += cash_amount
        balance_data["Assets"]["Current Assets"]["Accounts Receivable"] += receivable_amount
    with open("balance.json", "w") as file:
        json.dump(balance_data, file, indent=4)
    #update income statement
    with open("income_statement.json", "r") as file:
        income_statement = json.load(file)
        income_statement["Revenue"]["Sales"] += customer_price * amount
        income_statement["Revenue"]["COGS"] += cost
    with open("income_statement.json", "w") as file:
        json.dump(income_statement, file, indent=4)
    print(sale, receivable_amount, cash_amount, cost)
    #update inventory
    update_inventory(amount)
    #update history of invoices
    with open("invoice.json", "r") as file:
        invoice_history = json.load(file)

    cur_entry = {
        "date": get_time(),
        "customer": customer,
        "Quantity": amount,
        "Price/Part": customer_price,
        "total": customer_price * amount,
        "Receivable Amount": receivable_amount,
        "Received Receivable": 0
    }
    invoice_history.append(cur_entry)
    with open("invoice.json", "w") as file:
        json.dump(invoice_history, file, indent=4)

    return redirect('/')

@app.route("/process_PO", methods=["POST"])
def process_PO():
    part = request.form.get("vendor")
    amount = int(request.form.get("amount"))
    price_p_unit = float(get_cost(part))
    total_price = price_p_unit * amount

    #update Balance Sheet
    with open("balance.json", "r") as file:
        balance_data = json.load(file)

    balance_data["Assets"]["Current Assets"]["Inventory"] += total_price
    balance_data["Liabilities"]["Current Liabilities"]["Accounts Payable"] += total_price
    with open("balance.json", "w") as file:
        json.dump(balance_data, file, indent=4)

    #update income statement
        #no income statement updates for inventory purchases

    #update inventory
    add_PO_inventory(part, amount)
    #update PO history
    with open("purchase_order.json", "r") as file:
        PO_history = json.load(file)

    cur_entry = {
        "date": get_time(),
        "Part": part,
        "Price/Unit": price_p_unit,
        "Quantity": amount,
        "value": price_p_unit * amount,
        "Paid payable": 0
    }
    PO_history.append(cur_entry)
    with open("purchase_order.json", "w") as file:
        json.dump(PO_history, file, indent=4)

    return redirect('/')

@app.route("/update_time", methods=["POST"])
def update_time_based_events():
    advance_time()
    #now need to update all accounts payable (from PO) and receivable (from Invoice)
    with open("purchase_order.json", "r") as file:
        purchase_orders = json.load(file)

    today = get_time()
    today = datetime.strptime(today, "%m-%d-%Y")  # Convert the string to a datetime object

    for entry in purchase_orders:
        order_date = datetime.strptime(entry["date"], "%m-%d-%Y")

        if (today - order_date).days >= 28 and entry["Paid payable"] == 0:
            value = entry['value']
            with open("balance.json", "r") as file:
                balance_data = json.load(file)
                balance_data["Assets"]["Current Assets"]["Cash"] -= value
                balance_data["Liabilities"]["Current Liabilities"]["Accounts Payable"] -= value
            with open("balance.json", "w") as file:
                json.dump(balance_data, file, indent=4)
            entry["Paid payable"] = 1
    with open("purchase_order.json", "w") as file:
        json.dump(purchase_orders, file, indent=4)

    with open("invoice.json", "r") as file:
        invoices = json.load(file)
    for entry in invoices:
        order_date = datetime.strptime(entry["date"], "%m-%d-%Y")
        if (today - order_date).days >= 28 and entry["Received Receivable"] == 0:
            receivable_amount = entry["Receivable Amount"]
            with open("balance.json", "r") as file:
                balance_data = json.load(file)
                balance_data["Assets"]["Current Assets"]["Cash"] += receivable_amount
                balance_data["Assets"]["Current Assets"]["Accounts Receivable"] -= receivable_amount
            with open("balance.json", "w") as file:
                json.dump(balance_data, file, indent=4)
            entry["Received Receivable"] = 1
    with open("invoice.json", 'w') as file:
        json.dump(invoices, file, indent=4)

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
