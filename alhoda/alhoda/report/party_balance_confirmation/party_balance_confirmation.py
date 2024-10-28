# Copyright (c) 2024, Erpgulf and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Party Type"),
            "fieldname": "party_type",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Party"),
            "fieldname": "party",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Party Name"),
            "fieldname": "party_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Receivable Account"),
            "fieldname": "party_account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 150
        },
        {
            "label": _("Balance"),
            "fieldname": "balance",
            "fieldtype": "Currency",
            "width": 150
        }
    ]

def get_data(filters):
    conditions = []
    if filters.get("company"):
        conditions.append(f"gl.company = '{filters.get('company')}'")
    if filters.get("party_type"):
        conditions.append(f"gl.party_type = '{filters.get('party_type')}'")
    if filters.get("party"):
        party_list = "', '".join(filters.get("party"))
        conditions.append(f"gl.party IN ('{party_list}')")
    if filters.get("party_account"):
        conditions.append(f"gl.account = '{filters.get('party_account')}'")
    if filters.get("cost_center"):
        conditions.append(f"gl.cost_center = '{filters.get('cost_center')}'")
    if filters.get("report_date"):
        conditions.append(f"gl.posting_date <= '{filters.get('report_date')}'")
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT 
            gl.party_type AS party_type,
            gl.party AS party,
            party_name.`{filters.get("party_type")}_name` AS party_name,
            gl.account AS party_account,
            SUM(gl.debit - gl.credit) AS balance
        FROM `tabGL Entry` gl
        LEFT JOIN `tab{filters.get("party_type")}` party_name ON gl.party = party_name.name
        WHERE {where_clause}
        GROUP BY gl.party_type, gl.party, gl.account
        
    """
    data = frappe.db.sql(query, as_dict=True)
    
    # Add formatting for bold if required
    for row in data:
        row["bold"] = row["balance"] < 0  # Example condition to make balance negative bold
    
    return data
