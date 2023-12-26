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
        'fieldname': 'item_name',
        'label': 'Description',
        'fieldtype': 'Data',
        'width': 200
    },

    {
        'fieldname': 'warehouse',
        'label': ('Warehouse'),
        'fieldtype': 'Data',
        'align': 'left',
        'width': 100
    },

   

    {
        'fieldname': 'actual_qty',
        'label': ('Quantity'),
        'fieldtype': 'float',
        'width': 100,
        'align': 'right'
    },
        {
        'fieldname': 'reserved_qty',
        'label': ('Reserved Qty'),
        'fieldtype': 'float',
        'width': 100,
        'align': 'right'
    },
        {
        'fieldname': 'projected_qty',
        'label': ('Projected Qty'),
        'fieldtype': 'float',
        'width': 100,
        'align': 'right'

    },        

]
def get_data_and_chart(filters):
    conditions = "AND 1=1 "
    if(filters.get('item_code')):
        conditions += f"and  tb.item_code like '%{filters.get('item_code')}%'"
            
        
    
    
    mysql = f"""
SELECT
    tb.item_code,
    ti.item_name ,
    tb.warehouse,
    tb.actual_qty,
    tb.reserved_qty,
    tb.projected_qty
FROM
    `tabBin` tb
LEFT JOIN
    `tabItem` ti ON tb.item_code = ti.item_code
WHERE 1=1 {conditions}
GROUP BY
    tb.item_code, tb.warehouse
ORDER BY
    tb.item_code, tb.warehouse
"""

   
    data = frappe.db.sql(mysql, as_dict=True)
    return data
    
    


        
