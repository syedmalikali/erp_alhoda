import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate, formatdate, add_days
from erpnext.accounts.report.utils import get_currency

def execute(filters=None):
    if not filters:
        filters = {}
    
    validate_filters(filters)
    
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data, filters)
    report_summary = get_report_summary(data)
    message = get_message(filters)
    
    return columns, data, message, chart, report_summary

def validate_filters(filters):
    if not filters.get("company"):
        frappe.throw(_("Please select a Company"))
    
    if not filters.get("from_date"):
        filters.from_date = add_days(nowdate(), -30)
    
    if not filters.get("to_date"):
        filters.to_date = nowdate()
    
    if not filters.get("group_by"):
        filters.group_by = "Monthly"

def get_columns(filters):
    columns = []
    
    # Add grouping column based on filter
    if filters.group_by == "Daily":
        columns.append({
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        })
    elif filters.group_by == "Weekly":
        columns.append({
            "label": _("Week"),
            "fieldname": "week",
            "fieldtype": "Data",
            "width": 100
        })
    elif filters.group_by == "Monthly":
        columns.append({
            "label": _("Month"),
            "fieldname": "month",
            "fieldtype": "Data",
            "width": 100
        })
    elif filters.group_by == "Yearly":
        columns.append({
            "label": _("Year"),
            "fieldname": "year",
            "fieldtype": "Data",
            "width": 100
        })
    elif filters.group_by == "Salesman":
        columns.append({
            "label": _("Salesman"),
            "fieldname": "salesman",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 150
        })
    elif filters.group_by == "Cost Center":
        columns.append({
            "label": _("Cost Center"),
            "fieldname": "cost_center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 150
        })
    elif filters.group_by == "Invoice":
        columns.append({
            "label": _("Invoice"),
            "fieldname": "invoice",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 120
        })
    elif filters.group_by == "Item":
        columns.append({
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        })
    elif filters.group_by == "Item Group":
        columns.append({
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 150
        })
    
    # Add metrics columns
    columns.extend([
        {
            "label": _("Qty Sold"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Sales Amount"),
            "fieldname": "sales_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("Cost Amount"),
            "fieldname": "cost_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("Profit"),
            "fieldname": "profit",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("Profit %"),
            "fieldname": "profit_percent",
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "label": _("Currency"),
            "fieldname": "currency",
            "fieldtype": "Link",
            "options": "Currency",
            "width": 80,
            "hidden": 1
        }
    ])
    
    return columns

def get_data(filters):
    conditions = get_conditions(filters)
    currency = frappe.get_cached_value('Company', filters.company, 'default_currency')
    
    # Get sales data
    sales_data_query = """
        SELECT
            si.posting_date,
            si.name as invoice,
            si.base_grand_total as sales_amount,
            si.currency,
            si.cost_center,
            sit.item_code,
            sit.item_group,
            tst.sales_person as salesman,
            sit.qty,
            sit.base_net_amount as item_sales_amount,
            sit.dn_detail
        FROM
            `tabSales Invoice` si
        JOIN
            `tabSales Invoice Item` sit ON si.name = sit.parent
	JOIN 
	    `tabSales Team` tst on si.name = tst.parent	
        WHERE
            si.docstatus = 1
            {conditions}
        ORDER BY
            si.posting_date
    """.format(conditions=conditions)
    
    sales_data = frappe.db.sql(sales_data_query, filters, as_dict=1)
    
    # Calculate cost for each item
    for item in sales_data:
        cost_price = get_item_cost(item['item_code'], item['posting_date'], item['invoice'], item.get('dn_detail'))
        item['cost_amount'] = cost_price * item['qty'] if cost_price else 0
        item['profit'] = item['item_sales_amount'] - item['cost_amount']
        item['profit_percent'] = (item['profit'] / item['item_sales_amount'] * 100) if item['item_sales_amount'] else 0
    
    # Group data based on filters
    grouped_data = group_data(sales_data, filters)
    
    return grouped_data

def get_item_cost(item_code, posting_date, voucher_no, dn_detail=None):
    # Try to get cost from Stock Ledger Entry first
    sle_cost = frappe.db.sql("""
        SELECT valuation_rate
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s AND voucher_no = %s AND posting_date <= %s
        ORDER BY posting_date DESC, posting_time DESC, creation DESC
        LIMIT 1
    """, (item_code, voucher_no, posting_date))
    
    if sle_cost and sle_cost[0][0]:
        return flt(sle_cost[0][0])
    
    # If not found in SLE and dn_detail is available, check delivery note
    if dn_detail:
        # Get the delivery note from the dn_detail
        dn_name = frappe.db.get_value("Delivery Note Item", dn_detail, "parent")
        if dn_name:
            dn_cost = frappe.db.sql("""
                SELECT valuation_rate
                FROM `tabStock Ledger Entry`
                WHERE item_code = %s AND voucher_no = %s AND posting_date <= %s
                ORDER BY posting_date DESC, posting_time DESC, creation DESC
                LIMIT 1
            """, (item_code, dn_name, posting_date))
            
            if dn_cost and dn_cost[0][0]:
                return flt(dn_cost[0][0])
    
    # If still not found, get average valuation rate up to that date
    avg_cost = frappe.db.sql("""
        SELECT valuation_rate
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s AND posting_date <= %s
        ORDER BY posting_date DESC, posting_time DESC, creation DESC
        LIMIT 1
    """, (item_code, posting_date))
    
    return flt(avg_cost[0][0]) if avg_cost else 0

def group_data(data, filters):
    grouped = {}
    
    for item in data:
        # Create key based on group_by filter
        if filters.group_by == "Daily":
            key = str(item['posting_date'])
            label = formatdate(item['posting_date'])
        elif filters.group_by == "Weekly":
            week = get_week_of_year(item['posting_date'])
            key = f"{item['posting_date'].year}-W{week:02d}"
            label = f"Week {week}, {item['posting_date'].year}"
        elif filters.group_by == "Monthly":
            key = f"{item['posting_date'].year}-{item['posting_date'].month:02d}"
            label = f"{item['posting_date'].strftime('%B')} {item['posting_date'].year}"
        elif filters.group_by == "Yearly":
            key = str(item['posting_date'].year)
            label = str(item['posting_date'].year)
        elif filters.group_by == "Salesman":
            key = item.get('salesman', 'Not Specified')
            label = key
        elif filters.group_by == "Cost Center":
            key = item.get('cost_center', 'Not Specified')
            label = key
        elif filters.group_by == "Invoice":
            key = item.get('invoice', 'Not Specified')
            label = key
        elif filters.group_by == "Item":
            key = item.get('item_code', 'Not Specified')
            label = key
        elif filters.group_by == "Item Group":
            key = item.get('item_group', 'Not Specified')
            label = key
        else:
            key = "All"
            label = "All"
        
        if key not in grouped:
            grouped[key] = {
                'posting_date': item['posting_date'] if filters.group_by == "Daily" else None,
                'week': label if filters.group_by == "Weekly" else None,
                'month': label if filters.group_by == "Monthly" else None,
                'year': label if filters.group_by == "Yearly" else None,
                'salesman': item.get('salesman') if filters.group_by == "Salesman" else None,
                'cost_center': item.get('cost_center') if filters.group_by == "Cost Center" else None,
                'invoice': item.get('invoice') if filters.group_by == "Invoice" else None,
                'item_code': item.get('item_code') if filters.group_by == "Item" else None,
                'item_group': item.get('item_group') if filters.group_by == "Item Group" else None,
                'qty': 0,
                'sales_amount': 0,
                'cost_amount': 0,
                'profit': 0,
                'currency': item.get('currency')
            }
        
        grouped[key]['qty'] += item.get('qty', 0)
        grouped[key]['sales_amount'] += item.get('item_sales_amount', 0)
        grouped[key]['cost_amount'] += item.get('cost_amount', 0)
        grouped[key]['profit'] += item.get('profit', 0)
    
    # Calculate profit percentage for each group
    for key in grouped:
        if grouped[key]['sales_amount']:
            grouped[key]['profit_percent'] = (grouped[key]['profit'] / grouped[key]['sales_amount']) * 100
        else:
            grouped[key]['profit_percent'] = 0
    
    # Convert to list and sort
    result = list(grouped.values())
    
    if filters.group_by in ["Daily", "Weekly", "Monthly", "Yearly"]:
        if filters.group_by == "Daily":
            result.sort(key=lambda x: x['posting_date'])
        else:
            result.sort(key=lambda x: x['sales_amount'], reverse=True)
    else:
        result.sort(key=lambda x: x['sales_amount'], reverse=True)
    
    return result

def get_conditions(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
    if filters.get("company"):
        conditions.append("si.company = %(company)s")
    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
    if filters.get("salesman"):
        conditions.append("tst.sales_person = %(salesman)s")
    if filters.get("cost_center"):
        conditions.append("si.cost_center = %(cost_center)s")
    if filters.get("item_code"):
        conditions.append("sit.item_code = %(item_code)s")
    if filters.get("item_group"):
        conditions.append("sit.item_group = %(item_group)s")
    
    return " AND " + " AND ".join(conditions) if conditions else ""

def get_chart(data, filters):
    if not data:
        return None
    
    labels = []
    sales_datapoints = []
    cost_datapoints = []
    profit_datapoints = []
    
    for row in data:
        if filters.group_by == "Daily":
            labels.append(formatdate(row.get('posting_date')))
        elif filters.group_by == "Weekly":
            labels.append(row.get('week', 'Unknown'))
        elif filters.group_by == "Monthly":
            labels.append(row.get('month', 'Unknown'))
        elif filters.group_by == "Yearly":
            labels.append(row.get('year', 'Unknown'))
        elif filters.group_by == "Salesman":
            labels.append(row.get('salesman', 'Not Specified'))
        elif filters.group_by == "Cost Center":
            labels.append(row.get('cost_center', 'Not Specified'))
        elif filters.group_by == "Invoice":
            labels.append(row.get('invoice', 'Not Specified'))
        elif filters.group_by == "Item":
            labels.append(row.get('item_code', 'Not Specified'))
        elif filters.group_by == "Item Group":
            labels.append(row.get('item_group', 'Not Specified'))
        else:
            labels.append("All")
        
        sales_datapoints.append(row.get('sales_amount', 0))
        cost_datapoints.append(row.get('cost_amount', 0))
        profit_datapoints.append(row.get('profit', 0))
    
    # Limit to 15 items for better visualization
    limit = min(15, len(labels))
    
    chart = {
        "data": {
            "labels": labels[:limit],
            "datasets": [
                {
                    "name": "Sales Amount",
                    "values": sales_datapoints[:limit]
                },
                {
                    "name": "Cost Amount",
                    "values": cost_datapoints[:limit]
                },
                {
                    "name": "Profit",
                    "values": profit_datapoints[:limit]
                }
            ]
        },
        "type": "bar",
        "barOptions": {
            "stacked": False
        },
        "title": f"Sales Analysis by {filters.group_by}",
        "height": 300
    }
    
    return chart

def get_report_summary(data):
    if not data:
        return None
    
    total_sales = sum([row.get('sales_amount', 0) for row in data])
    total_cost = sum([row.get('cost_amount', 0) for row in data])
    total_profit = sum([row.get('profit', 0) for row in data])
    total_qty = sum([row.get('qty', 0) for row in data])
    avg_profit_percent = (total_profit / total_sales * 100) if total_sales else 0
    
    return [
        {
            "value": total_sales,
            "label": "Total Sales",
            "datatype": "Currency",
            "currency": data[0].get('currency') if data else "USD"
        },
        {
            "value": total_cost,
            "label": "Total Cost",
            "datatype": "Currency",
            "currency": data[0].get('currency') if data else "USD"
        },
        {
            "value": total_profit,
            "label": "Total Profit",
            "datatype": "Currency",
            "currency": data[0].get('currency') if data else "USD"
        },
        {
            "value": avg_profit_percent,
            "label": "Avg Profit %",
            "datatype": "Percent"
        },
        {
            "value": total_qty,
            "label": "Total Qty",
            "datatype": "Float"
        }
    ]

def get_message(filters):
    if filters.get("group_by"):
        return _("Grouped by {0}").format(filters["group_by"])
    return ""

def get_week_of_year(date):
    return date.isocalendar()[1]