# Copyright (c) 2024, Erpgulf and contributors
# For license information, please see license.txt

import frappe


# def execute(filters=None):
#	columns, data = [], []
#	return columns, data

from datetime import datetime
@frappe.whitelist()
def execute(filters=None):
    
    columns = get_columns()
    data = get_data(filters)

    
    return columns, data, cs_data

def get_columns():
    return [
        {
            'fieldname': 'company',
            'label': 'Company',
            'fieldtype': 'Data',
        },
        {
            'fieldname': 'item_code',
            'label': 'Item Code',
            'fieldtype': 'Data',
        },
        {
            'fieldname': 'item_name',
            'label': 'Item Name',
            'fieldtype': 'Data',
        },
        {
            'fieldname': 'qty',
            'label': 'Quantity',
            'fieldtype': 'Float',
        },
        {
            'fieldname': 'amount',
            'label': 'Amount',
            'fieldtype': 'Currency',
        }
    ]



def get_data(filters):
    conditions = []

    if filters.get("posting_date"):
        conditions.append("si.posting_date = %(posting_date)s")
    if filters.get("due_date"):
        conditions.append("si.due_date <= %(due_date)s")
    if filters.get("item_group"):
        conditions.append("si_item.item_group = %(item_group)s")
    
    

    query = """
        SELECT 
            si.company,
            si_item.item_code, 
            si_item.item_name, 
            si_item.qty, 
            si_item.amount
        FROM 
            `tabSales Invoice Item` si_item
        JOIN 
            `tabSales Invoice` si 
        ON 
            si.name = si_item.parent
        WHERE 
            {conditions}
    """.format(conditions=conditions)
    frappe.errprint(query)

    data = frappe.db.sql(query, filters, as_dict=True)
    
    return data