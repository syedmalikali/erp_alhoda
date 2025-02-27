from __future__ import unicode_literals
import frappe
from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import (
    execute as accounts_receivable_summary,
    AccountsReceivableSummary,
)

def execute(filters=None):
    return extend_report(accounts_receivable_summary, filters)

def extend_report(base_execute, filters):
    base_result = base_execute(filters)
    columns, data = base_result[0], base_result[1]
    # Extend columns to add the Customer Name
    columns = _extend_columns(columns)
    # Extend data to include Customer Name
    extended_data = _extend_data(filters, data)
    return columns, extended_data, None

def _extend_columns(columns):
    if columns:  # Ensure the list is not empty
        columns.pop(0)  # Removes the first column
        columns[0]["width"] = 100  # Set the width of the first column
    # Add the 'Customer Name' column after 'Party' column or as needed
    columns.insert(1, {
        "label": "Customer Name",
        "fieldname": "customer_name",
        "fieldtype": "Link",
        "options": "Customer",
        "width": 300
    })
    return columns

def _extend_data(filters, data):
    # Extend each row of data by adding the 'Customer Name'
    for entry in data:
        if entry.get("party"):  # Assuming 'party' is the customer ID or link
            customer_name = get_customer_name(entry.get("party"))
            entry["customer_name"] = customer_name
    return data

def get_customer_name(customer_id):
    from frappe import db
    return db.get_value("Customer", customer_id, "customer_name")
