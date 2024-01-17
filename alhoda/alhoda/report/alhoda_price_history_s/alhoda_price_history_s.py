# Copyright (c) 2024, Erpgulf and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data_and_chart(filters)
    return columns, data
def get_columns():
    return [ 
    {
        'fieldname': 'branch',
        'label': ('Branch'),
        'fieldtype': 'Link',
        'options': 'Cost Center',
        'width': 100
    },
    {
        'fieldname': 'item_code',
        'label': ('Item Code'),
        'fieldtype': 'Data',
        'options': 'Item',
        'width': 200
    },


    {
        'fieldname': 'customer_name',
        'label': ('Customer Name'),
        'fieldtype': 'Data',
        'align': 'left',
        'width': 200
    },

   

    {
        'fieldname': 'qty',
        'label': ('Quantity'),
        'fieldtype': 'Data',
        'width': 100,
        'align': 'center'
    },
        {
        'fieldname': 'unit_price',
        'label': ('Selling Price'),
        'fieldtype': 'Currency',
        'width': 175,
        'align': 'right'
    },
        {
        'fieldname': 'customer_po_number',
        'label': ('PO Number'),
        'fieldtype': 'Data',
        'width': 200,
        'align': 'left'

    },        

]
def get_data_and_chart(filters):
    conditions = "AND 1=1 "
    if(filters.get('customer')):
        conditions += f"and  customer_name = '%{filters.get('customer_name')}%'"
        
    if(filters.get('item_code')):
        conditions += f"and  item_code like '%{filters.get('item_code')}%'"

    if(filters.get('branch')):
        conditions += f"and  branch like '%{filters.get('branch')}%'"
  
        
    
    
    mysql = f"""SELECT
    branch,
    customer_name,
    item_code,
    unit_price,
    qty,
    unit_cost,
    customer_po_number,
    invoice_number,
    invoice_date,
    invoice_type
FROM
    `tabAlhoda Price History`
WHERE 
    1=1 {conditions}
"""

    
    data = frappe.db.sql(mysql, as_dict=True)
    return data
