import frappe
import pandas as pd
import decimal
from datetime import date, datetime

def execute(filters=None):
    filters = frappe._dict(filters or {})

    # --- Default Filters ---
    if not filters.from_date or not filters.to_date:
        frappe.throw("Please select From Date and To Date")

    group_by_field = get_group_field(filters.group_by)

    # --- Query Data ---
    data = frappe.db.sql(f"""
        SELECT
            si.name AS invoice,
            MONTH(si.posting_date) AS month,
            MONTHNAME(si.posting_date) AS month_name,
            YEAR(si.posting_date) AS year,
            sii.net_amount AS total,
            {group_by_field} AS group_name
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE si.docstatus = 1
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=True)

    if not data:
        return [], []

    # --- Clean Data for Pandas ---
    clean_data = []
    for row in data:
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, decimal.Decimal):
                v = float(v)
            elif isinstance(v, (date, datetime)):
                v = v.strftime("%Y-%m-%d")
            clean_row[k] = v
        clean_data.append(clean_row)

    # --- Build DataFrame ---
    df = pd.DataFrame(clean_data)
    df["month_label"] = df["month_name"].str.slice(0, 3) + " " + df["year"].astype(str)

    # --- Pivot Table (trend) ---
    pivot = df.pivot_table(
        index="group_name",
        columns="month_label",
        values="total",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    # --- Sort Months Chronologically ---
    pivot = pivot[[pivot.columns[0]] + sorted(pivot.columns[1:], key=lambda x: month_sort_key(x))]

    # --- Build Columns ---
    columns = [{"label": filters.group_by, "fieldname": "group_name", "fieldtype": "Data", "width": 200}]
    for month in pivot.columns[1:]:
        columns.append({
            "label": month,
            "fieldname": month,
            "fieldtype": "Currency",
            "width": 120
        })

    # --- Convert to List for Frappe ---
    result = pivot.to_dict("records")

    # --- Chart Data ---
    chart = {
        "data": {
            "labels": list(pivot.columns[1:]),
            "datasets": [
                {
                    "name": row["group_name"],
                    "values": [row[m] for m in pivot.columns[1:]]
                }
                for _, row in pivot.iterrows()
            ]
        },
        "type": "line" if len(pivot) <= 5 else "bar",
        "height": 400
    }

    return columns, result, None, chart


# --- Helper to get actual DB field based on group type ---
def get_group_field(group_by):
    mapping = {
        "Customer": "si.customer",
        "Item": "sii.item_code",
        "Item Group": "sii.item_group",
        "Cost Center": "sii.cost_center",
        "Warehouse": "sii.warehouse",
        "POS Profile": "si.pos_profile",
        "Territory": "si.territory",
    }
    if not group_by or group_by not in mapping:
        frappe.throw("Please select a valid 'Group By' option.")
    return mapping[group_by]


# --- Helper for sorting months correctly ---
def month_sort_key(label):
    try:
        parts = label.split(" ")
        month_abbr = parts[0]
        year = int(parts[1])
        month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        return (year, month_order.index(month_abbr))
    except Exception:
        return (9999, 99)
