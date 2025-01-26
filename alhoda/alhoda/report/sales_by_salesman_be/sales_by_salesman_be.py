# Copyright (c) 2025, Erpgulf and contributors
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
        {'fieldname': 'branch', 'label': _('Sman'), 'fieldtype': 'Data', 'width': 150},
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

#    if filters.get('date_range'):
#        from_date, to_date = frappe.utils.get_timespan_date_range(filters['date_range'])
    conditions = f"AND si.posting_date BETWEEN '{from_date}' AND '{to_date}'"
    
    query = f"""
        SELECT 
            CASE 
                WHEN st.sales_person = 'CS' THEN 'Kho Counter'
                WHEN st.sales_person = 'JNB' THEN 'Babu'
                WHEN st.sales_person = 'EM' THEN 'Ebi'
                WHEN st.sales_person = 'FM' THEN 'Farhan'
                WHEN st.sales_person = 'JIH' THEN 'Ismath'
                WHEN st.sales_person = 'RCS' THEN 'Riyad Counter'
                WHEN st.sales_person = 'RMK' THEN 'Kathafy'
            END AS branch,
            SUM(si.net_total) AS tot,
            SUM(CASE WHEN MONTH(si.posting_date) = 1 THEN si.net_total ELSE 0 END) AS jan,
            SUM(CASE WHEN MONTH(si.posting_date) = 2 THEN si.net_total ELSE 0 END) AS feb,
            SUM(CASE WHEN MONTH(si.posting_date) = 3 THEN si.net_total ELSE 0 END) AS mar,
            SUM(CASE WHEN MONTH(si.posting_date) = 4 THEN si.net_total ELSE 0 END) AS apr,
            SUM(CASE WHEN MONTH(si.posting_date) = 5 THEN si.net_total ELSE 0 END) AS may,
            SUM(CASE WHEN MONTH(si.posting_date) = 6 THEN si.net_total ELSE 0 END) AS jun,
            SUM(CASE WHEN MONTH(si.posting_date) = 7 THEN si.net_total ELSE 0 END) AS jul,
            SUM(CASE WHEN MONTH(si.posting_date) = 8 THEN si.net_total ELSE 0 END) AS aug,
            SUM(CASE WHEN MONTH(si.posting_date) = 9 THEN si.net_total ELSE 0 END) AS sep,
            SUM(CASE WHEN MONTH(si.posting_date) = 10 THEN si.net_total ELSE 0 END) AS oct,
            SUM(CASE WHEN MONTH(si.posting_date) = 11 THEN si.net_total ELSE 0 END) AS nov,
            SUM(CASE WHEN MONTH(si.posting_date) = 12 THEN si.net_total ELSE 0 END) AS dec1
        FROM 
            `tabSales Invoice` si
        LEFT JOIN 
            `tabSales Team` st ON st.parent = si.name
        WHERE 
            si.docstatus = 1 {conditions}
        GROUP BY 
            st.sales_person
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
        # Check if date_range is valid 
        date_range = filters.get("date_range")
        frappe.errprint('malik')
        frappe.errprint(date_range)
        #if date_range not in ["this_year", "last_year", "this_month", "last_month"]:
            #frappe.throw(f"Invalid date range: {date_range}")
        
        # Use frappe.utils.get_timespan_date_range for predefined ranges
        # from_date, to_date = frappe.utils.get_timespan_date_range(date_range)
        from_date, to_date = get_timespan_date_range(filters.get("date_range").lower())
        frappe.errprint(from_date)
        frappe.errprint(to_date)


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
