# Copyright (c) 2023, Erpgulf and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_timespan_date_range

def execute(filters=None):
    filters = filters or {}
    frappe.errprint(f"Filters: {filters}") 

    # Ensure that the date_range filter is passed and is valid
    if "date_range" not in filters:
        frappe.throw("Date Range filter is missing.")

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)

    return columns, data, None, chart

def get_columns():
    return [
        {'fieldname': 'branch', 'label': _('Branch'), 'fieldtype': 'Data', 'width': 150},
        {'fieldname': 'tot', 'label': _('Total'), 'fieldtype': 'Currency', 'width': 120},
        {'fieldname': 'jan', 'label': _('Jan'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'feb', 'label': _('Feb'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'mar', 'label': _('Mar'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'apr', 'label': _('Apr'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'may', 'label': _('May'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'jun', 'label': _('Jun'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'jul', 'label': _('Jul'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'aug', 'label': _('Aug'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'sep', 'label': _('Sep'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'oct', 'label': _('Oct'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'nov', 'label': _('Nov'), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'dec1', 'label': _('Dec'), 'fieldtype': 'Currency', 'width': 100},
    ]

def get_data(filters):
    conditions = ""
    if not filters.get("date_range"):
        frappe.throw("Please select a valid Date Range.")

    # Unpack the date_range
    from_date, to_date = get_date_range(filters)

    conditions = f"AND si.posting_date BETWEEN '{from_date}' AND '{to_date}'"

    query = f"""
        SELECT 
            cost_center AS branch,
            SUM(IF(grand_total, grand_total, 0)) AS tot,
            SUM(IF(MONTH(posting_date) = 1, grand_total, 0)) AS jan,
            SUM(IF(MONTH(posting_date) = 2, grand_total, 0)) AS feb,
            SUM(IF(MONTH(posting_date) = 3, grand_total, 0)) AS mar,
            SUM(IF(MONTH(posting_date) = 4, grand_total, 0)) AS apr,
            SUM(IF(MONTH(posting_date) = 5, grand_total, 0)) AS may,
            SUM(IF(MONTH(posting_date) = 6, grand_total, 0)) AS jun,
            SUM(IF(MONTH(posting_date) = 7, grand_total, 0)) AS jul,
            SUM(IF(MONTH(posting_date) = 8, grand_total, 0)) AS aug,
            SUM(IF(MONTH(posting_date) = 9, grand_total, 0)) AS sep,
            SUM(IF(MONTH(posting_date) = 10, grand_total, 0)) AS oct,
            SUM(IF(MONTH(posting_date) = 11, grand_total, 0)) AS nov,
            SUM(IF(MONTH(posting_date) = 12, grand_total, 0)) AS dec1
        FROM 
            `tabSales Invoice` si
        WHERE 
            si.docstatus = 1 {conditions}
        GROUP BY 
            cost_center
        ORDER BY 
            tot DESC
    """
    frappe.errprint(query)
    return frappe.db.sql(query, as_dict=True)

def get_date_range(filters):
    if filters.get("date_range") == "custom":
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")
        if not (from_date and to_date):
            frappe.throw("Please select both From Date and To Date for Custom Range")
    else:
        # Use frappe.utils.get_timespan_date_range for predefined ranges
        from_date, to_date = get_timespan_date_range(filters.get("date_range").lower())

    return from_date, to_date

def get_chart_data(data):
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    datasets = []

    for row in data:
        datasets.append({
            'name': row['branch'],
            'values': [row['jan'], row['feb'], row['mar'], row['apr'], row['may'], row['jun'], 
                       row['jul'], row['aug'], row['sep'], row['oct'], row['nov'], row['dec1']]
        })

    return {
        'data': {
            'labels': labels,
            'datasets': datasets,
        },
        'type': 'bar',
    }
