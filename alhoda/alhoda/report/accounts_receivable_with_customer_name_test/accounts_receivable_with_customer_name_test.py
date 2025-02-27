import frappe
from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import get_data

def get_data_with_customer(filters):
    data = get_data(filters)
    for row in data:
        if row.get("party_type") == "Customer":
            customer = frappe.db.get_value("Customer", row["party"], "customer_name")
            row["customer_name"] = customer or ""
    return data
