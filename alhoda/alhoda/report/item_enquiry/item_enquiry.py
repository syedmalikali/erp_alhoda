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
        'width': 300
    },

    {
        'fieldname': 'warehouse',
        'label': ('Warehouse'),
        'fieldtype': 'Data',
        'align': 'left',
        'width': 100
    },

    {
        'fieldname': 'valuation_rate',
        'label': ('Avg.Cost'),
        'fieldtype': 'Currency',
        'width': 100,
        'disable_total':True,
        
        'align': 'right'
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
  {
        'fieldname': 'custom_part_number',
        'label': ('Part Number'),
        'fieldtype': 'Data',
        'width': 200,
        'align': 'center'

    },          

]
def get_data_and_chart(filters):
    conditions = "AND 1=1 "
    cond2 = " "
    if(filters.get('item_code')):
        conditions += f" and  tb.item_code like '%{filters.get('item_code')}%'"
    if(filters.get('description')):
        conditions += f"and  ti.item_name like '%{filters.get('description')}%'"
    if(filters.get('hide_zero_qty')):
        conditions += f" and  tb.actual_qty>0"
    if(filters.get('custom_part_number')):
        conditions += f" and  ti.custom_part_number like '%{filters.get('custom_part_number')}%'"

    if not (filters.get('item_code') or filters.get('description') ):
        cond2 = "limit 200"    
            
        
    
    
    mysql = f"""
SELECT
    tb.item_code,
    ti.item_name ,
    tb.warehouse,
    tb.valuation_rate,
    tb.actual_qty,
    tb.reserved_qty,
    tb.projected_qty,
    ti.custom_part_number 
FROM
    `tabBin` tb
LEFT JOIN
    `tabItem` ti ON tb.item_code = ti.item_code
WHERE 1=1 {conditions}
GROUP BY
    tb.item_code, tb.warehouse
ORDER BY
    tb.item_code, tb.warehouse
{cond2}
"""

    frappe.errprint(mysql)
    data = frappe.db.sql(mysql, as_dict=True)
    return data
    
    


        
