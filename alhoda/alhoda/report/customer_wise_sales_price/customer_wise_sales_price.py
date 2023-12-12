# Copyright (c) 2023, Erpgulf and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data_and_chart(filters)
    return columns, data
def get_columns():
    return [ 
    {
        'fieldname': 'item_code',
        'label': ('Item Code'),
        'fieldtype': 'Data',
        'options': 'Item',
        'width': 200
    },

    {
        'fieldname': 'posting_date',
        'label': ('Date'),
        'fieldtype': 'Date',
        'width': 125
    },

    {
        'fieldname': 'customer_name',
        'label': ('Customer Name'),
        'fieldtype': 'Data',
        'align': 'left',
        'width': 200
    },

    {
        'fieldname': 'name',
        'label': ('Invoice Number'),
        'fieldtype': 'Link',
        'width': 200,
        'options': 'Sales Invoice',
        'align': 'left'
    },    

    {
        'fieldname': 'qty',
        'label': ('Quantity'),
        'fieldtype': 'Data',
        'width': 100,
        'align': 'center'
    },
        {
        'fieldname': 'rate',
        'label': ('Selling Price'),
        'fieldtype': 'Currency',
        'width': 175,
        'align': 'right'
    },
        {
        'fieldname': 'po_no',
        'label': ('PO Number'),
        'fieldtype': 'Data',
        'width': 200,
        'align': 'left'

    },        

]
def get_data_and_chart(filters):
    conditions = "AND 1=1 "
    if(filters.get('customer')):
        conditions += f"and  si.customer = '{filters.get('customer')}'"
        
    if(filters.get('item_code')):
        conditions += f"and  sit.item_code like '%{filters.get('item_code')}%'"
    if (filters.get('from_date')):
        conditions += f"AND posting_date between '{filters.get('from_date')}' and '{filters.get('to_date')}'"
            
        
    
    
    mysql = f"""SELECT 
    sit.item_code,si.posting_date, si.customer_name, si.name, sit.qty, sit.rate,si.po_no 
FROM 
    `tabSales Invoice` si 
JOIN 
    `tabSales Invoice Item` sit ON `si`.`name` = `sit`.`parent`
WHERE 
    1=1 {conditions}
"""

    
    data = frappe.db.sql(mysql, as_dict=True)
    return data
    
    


        
