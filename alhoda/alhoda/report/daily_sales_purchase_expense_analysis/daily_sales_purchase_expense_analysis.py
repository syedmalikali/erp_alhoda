# File 1: daily_sales_purchase_expense_analysis.py
# Place this in: custom_app/custom_app/report/daily_sales_purchase_expense_analysis/

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_days, formatdate, cint
import json
from datetime import datetime, timedelta

def execute(filters=None):
    """Main execution function for the report"""
    if not filters:
        filters = {}
    
    # Validate filters
    validate_filters(filters)
    
    # Get columns
    columns = get_columns(filters)
    
    # Get data
    data = get_data(filters)
    
    # Get chart data
    chart = get_chart_data(data, filters)
    
    # Get summary data
    summary = get_summary_data(data, filters)
    
    return columns, data, None, chart, summary

def validate_filters(filters):
    """Validate and set default filters"""
    if not filters.get("from_date"):
        filters["from_date"] = add_days(frappe.utils.today(), -30)
    
    if not filters.get("to_date"):
        filters["to_date"] = frappe.utils.today()
    
    if not filters.get("company"):
        filters["company"] = frappe.defaults.get_user_default("Company")

def get_columns(filters):
    """Define report columns"""
    columns = [
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Day"),
            "fieldname": "day_name",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": _("Sales Amount"),
            "fieldname": "sales_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Sales Count"),
            "fieldname": "sales_count",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Purchase Amount"),
            "fieldname": "purchase_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Purchase Count"),
            "fieldname": "purchase_count",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Expense Amount"),
            "fieldname": "expense_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Expense Count"),
            "fieldname": "expense_count",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Net Profit/Loss"),
            "fieldname": "net_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Profit Margin %"),
            "fieldname": "profit_margin",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": _("Cash Flow"),
            "fieldname": "cash_flow",
            "fieldtype": "Currency",
            "width": 120
        }
    ]
    return columns

def get_data(filters):
    """Get main report data"""
    # Generate date range
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    
    data = []
    current_date = from_date
    
    while current_date <= to_date:
        date_str = formatdate(current_date, "yyyy-mm-dd")
        
        # Get sales data
        sales_data = get_sales_data(date_str, filters)
        
        # Get purchase data  
        purchase_data = get_purchase_data(date_str, filters)
        
        # Get expense data
        expense_data = get_expense_data(date_str, filters)
        
        # Calculate derived metrics
        sales_amount = flt(sales_data.get("amount", 0))
        purchase_amount = flt(purchase_data.get("amount", 0))
        expense_amount = flt(expense_data.get("amount", 0))
        
        net_amount = sales_amount - purchase_amount - expense_amount
        profit_margin = (net_amount / sales_amount * 100) if sales_amount > 0 else 0
        cash_flow = sales_amount - purchase_amount - expense_amount
        
        row = {
            "date": current_date,
            "day_name": current_date.strftime("%A"),
            "sales_amount": sales_amount,
            "sales_count": cint(sales_data.get("count", 0)),
            "purchase_amount": purchase_amount,
            "purchase_count": cint(purchase_data.get("count", 0)),
            "expense_amount": expense_amount,
            "expense_count": cint(expense_data.get("count", 0)),
            "net_amount": net_amount,
            "profit_margin": profit_margin,
            "cash_flow": cash_flow
        }
        
        data.append(row)
        current_date = add_days(current_date, 1)
    
    return data

def get_sales_data(date, filters):
    """Get sales data for a specific date"""
    conditions = get_conditions(filters, "si")
    
    sales_data = frappe.db.sql(f"""
        SELECT 
            COALESCE(SUM(si.grand_total), 0) as amount,
            COUNT(si.name) as count
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1 
        AND DATE(si.posting_date) = %s
        {conditions}
    """, (date,), as_dict=True)
    
    return sales_data[0] if sales_data else {"amount": 0, "count": 0}

def get_purchase_data(date, filters):
    """Get purchase data for a specific date"""
    conditions = get_conditions(filters, "pi")
    
    purchase_data = frappe.db.sql(f"""
        SELECT 
            COALESCE(SUM(pi.grand_total), 0) as amount,
            COUNT(pi.name) as count
        FROM `tabPurchase Invoice` pi
        WHERE pi.docstatus = 1 
        AND DATE(pi.posting_date) = %s
        {conditions}
    """, (date,), as_dict=True)
    
    return purchase_data[0] if purchase_data else {"amount": 0, "count": 0}

def get_expense_data(date, filters):
    """Get expense data for a specific date"""
    conditions = get_conditions(filters, "er")
    
    expense_data = frappe.db.sql(f"""
        SELECT 
            COALESCE(SUM(er.total_sanctioned_amount), 0) as amount,
            COUNT(er.name) as count
        FROM `tabExpense Claim` er
        WHERE er.docstatus = 1 
        AND DATE(er.posting_date) = %s
        {conditions}
        
        UNION ALL
        
        SELECT 
            COALESCE(SUM(je.total_debit), 0) as amount,
            COUNT(je.name) as count
        FROM `tabJournal Entry` je
        JOIN `tabJournal Entry Account` jea ON je.name = jea.parent
        WHERE je.docstatus = 1 
        AND je.voucher_type = 'Journal Entry'
        AND DATE(je.posting_date) = %s
        AND jea.account IN (
            SELECT name FROM `tabAccount` 
            WHERE account_type = 'Expense' 
            AND company = %s
        )
        {conditions.replace('er.', 'je.')}
    """, (date, date, filters.get("company")), as_dict=True)
    
    total_amount = sum(flt(row.get("amount", 0)) for row in expense_data)
    total_count = sum(cint(row.get("count", 0)) for row in expense_data)
    
    return {"amount": total_amount, "count": total_count}

def get_conditions(filters, alias):
    """Build SQL conditions based on filters"""
    conditions = ""
    
    if filters.get("company"):
        conditions += f" AND {alias}.company = '{filters.get('company')}'"
    
    if filters.get("cost_center"):
        conditions += f" AND {alias}.cost_center = '{filters.get('cost_center')}'"
    
    return conditions

def get_chart_data(data, filters):
    """Generate chart data for visualization"""
    if not data:
        return None
    
    # Prepare data for charts
    dates = [formatdate(row["date"], "dd MMM") for row in data]
    sales_amounts = [flt(row["sales_amount"]) for row in data]
    purchase_amounts = [flt(row["purchase_amount"]) for row in data]
    expense_amounts = [flt(row["expense_amount"]) for row in data]
    net_amounts = [flt(row["net_amount"]) for row in data]
    
    # Main trend chart
    chart = {
        "data": {
            "labels": dates,
            "datasets": [
                {
                    "name": "Sales",
                    "values": sales_amounts,
                    "chartType": "line"
                },
                {
                    "name": "Purchase", 
                    "values": purchase_amounts,
                    "chartType": "line"
                },
                {
                    "name": "Expense",
                    "values": expense_amounts,
                    "chartType": "line"
                },
                {
                    "name": "Net P&L",
                    "values": net_amounts,
                    "chartType": "line"
                }
            ]
        },
        "type": "axis-mixed",
        "height": 400,
        "colors": ["#28a745", "#dc3545", "#ffc107", "#007bff"],
        "axisOptions": {
            "xIsSeries": 1
        },
        "lineOptions": {
            "regionFill": 1
        }
    }
    
    return chart

def get_summary_data(data, filters):
    """Generate summary statistics"""
    if not data:
        return []
    
    # Calculate totals and averages
    total_sales = sum(flt(row["sales_amount"]) for row in data)
    total_purchase = sum(flt(row["purchase_amount"]) for row in data)
    total_expense = sum(flt(row["expense_amount"]) for row in data)
    total_net = sum(flt(row["net_amount"]) for row in data)
    
    avg_sales = total_sales / len(data) if data else 0
    avg_purchase = total_purchase / len(data) if data else 0
    avg_expense = total_expense / len(data) if data else 0
    avg_net = total_net / len(data) if data else 0
    
    # Calculate growth rates (comparing first and last periods)
    first_half = data[:len(data)//2] if len(data) > 7 else data[:3]
    second_half = data[len(data)//2:] if len(data) > 7 else data[3:]
    
    first_half_sales = sum(flt(row["sales_amount"]) for row in first_half) / len(first_half) if first_half else 0
    second_half_sales = sum(flt(row["sales_amount"]) for row in second_half) / len(second_half) if second_half else 0
    
    sales_growth = ((second_half_sales - first_half_sales) / first_half_sales * 100) if first_half_sales > 0 else 0
    
    # Best and worst performing days
    best_day = max(data, key=lambda x: x["net_amount"]) if data else {}
    worst_day = min(data, key=lambda x: x["net_amount"]) if data else {}
    
    summary = [
        {
            "label": _("Period Summary"),
            "value": f"{formatdate(filters.get('from_date'))} to {formatdate(filters.get('to_date'))}",
            "indicator": "blue"
        },
        {
            "label": _("Total Sales"),
            "value": f"?{total_sales:,.2f}",
            "indicator": "green"
        },
        {
            "label": _("Total Purchase"),
            "value": f"?{total_purchase:,.2f}",
            "indicator": "red"
        },
        {
            "label": _("Total Expenses"),
            "value": f"?{total_expense:,.2f}",
            "indicator": "orange"
        },
        {
            "label": _("Net Profit/Loss"),
            "value": f"?{total_net:,.2f}",
            "indicator": "green" if total_net >= 0 else "red"
        },
        {
            "label": _("Average Daily Sales"),
            "value": f"?{avg_sales:,.2f}",
            "indicator": "blue"
        },
        {
            "label": _("Sales Growth Rate"),
            "value": f"{sales_growth:+.1f}%",
            "indicator": "green" if sales_growth >= 0 else "red"
        },
        {
            "label": _("Best Performing Day"),
            "value": f"{formatdate(best_day.get('date', ''))} (?{best_day.get('net_amount', 0):,.2f})",
            "indicator": "green"
        },
        {
            "label": _("Worst Performing Day"),
            "value": f"{formatdate(worst_day.get('date', ''))} (?{worst_day.get('net_amount', 0):,.2f})",
            "indicator": "red"
        }
    ]
    
    return summary

# Additional utility functions for advanced analytics
def get_weekly_comparison(data):
    """Compare week-over-week performance"""
    weekly_data = {}
    for row in data:
        week_key = row["date"].isocalendar()[1]  # Get week number
        if week_key not in weekly_data:
            weekly_data[week_key] = {
                "sales": 0, "purchase": 0, "expense": 0, "days": 0
            }
        weekly_data[week_key]["sales"] += flt(row["sales_amount"])
        weekly_data[week_key]["purchase"] += flt(row["purchase_amount"])
        weekly_data[week_key]["expense"] += flt(row["expense_amount"])
        weekly_data[week_key]["days"] += 1
    
    return weekly_data

def get_day_wise_analysis(data):
    """Analyze performance by day of week"""
    day_analysis = {}
    for row in data:
        day = row["day_name"]
        if day not in day_analysis:
            day_analysis[day] = {
                "sales": [], "purchase": [], "expense": [], "net": []
            }
        day_analysis[day]["sales"].append(flt(row["sales_amount"]))
        day_analysis[day]["purchase"].append(flt(row["purchase_amount"]))
        day_analysis[day]["expense"].append(flt(row["expense_amount"]))
        day_analysis[day]["net"].append(flt(row["net_amount"]))
    
    # Calculate averages for each day
    for day in day_analysis:
        for metric in day_analysis[day]:
            values = day_analysis[day][metric]
            day_analysis[day][f"avg_{metric}"] = sum(values) / len(values) if values else 0
    
    return day_analysis

@frappe.whitelist()
def get_additional_charts(filters=None):
    """Get additional chart data for dashboard widgets"""
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    # Get main data
    data = get_data(filters)
    
    # Weekly comparison chart
    weekly_data = get_weekly_comparison(data)
    weekly_chart = {
        "data": {
            "labels": [f"Week {week}" for week in weekly_data.keys()],
            "datasets": [{
                "name": "Weekly Sales",
                "values": [weekly_data[week]["sales"] for week in weekly_data.keys()]
            }]
        },
        "type": "bar",
        "height": 300,
        "colors": ["#28a745"]
    }
    
    # Day-wise performance chart
    day_data = get_day_wise_analysis(data)
    day_chart = {
        "data": {
            "labels": list(day_data.keys()),
            "datasets": [{
                "name": "Average Sales",
                "values": [day_data[day]["avg_sales"] for day in day_data.keys()]
            }]
        },
        "type": "bar",
        "height": 300,
        "colors": ["#007bff"]
    }
    
    # Expense breakdown pie chart
    total_purchase = sum(flt(row["purchase_amount"]) for row in data)
    total_expense = sum(flt(row["expense_amount"]) for row in data)
    
    expense_chart = {
        "data": {
            "labels": ["Purchases", "Other Expenses"],
            "datasets": [{
                "values": [total_purchase, total_expense]
            }]
        },
        "type": "pie",
        "height": 300,
        "colors": ["#dc3545", "#ffc107"]
    }
    
    return {
        "weekly_chart": weekly_chart,
        "day_chart": day_chart, 
        "expense_chart": expense_chart,
        "summary_stats": {
            "total_days": len(data),
            "profitable_days": len([row for row in data if flt(row["net_amount"]) > 0]),
            "avg_daily_sales": sum(flt(row["sales_amount"]) for row in data) / len(data) if data else 0,
            "best_sales_day": max(data, key=lambda x: x["sales_amount"])["date"] if data else None
        }
    }