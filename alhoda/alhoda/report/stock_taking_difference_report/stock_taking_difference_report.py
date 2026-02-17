import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "S.No", "fieldname": "sno", "fieldtype": "Int", "width": 60},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 180},
        {"label": "System Qty", "fieldname": "system_qty", "fieldtype": "Float", "width": 110},
        {"label": "Inventory Qty", "fieldname": "inventory_qty", "fieldtype": "Float", "width": 120},
        {"label": "Difference", "fieldname": "difference", "fieldtype": "Float", "width": 100},
        {"label": "Cost", "fieldname": "cost", "fieldtype": "Currency", "width": 100},
        {"label": "Diff Value", "fieldname": "diff_value", "fieldtype": "Currency", "width": 120},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 200},
        {"label": "Tag", "fieldname": "tag", "fieldtype": "Data", "hidden": 1},
    ]


def get_data(filters):
    if not filters or not filters.get("stock_taking_summary"):
        frappe.throw("Please select Stock Taking Summary")

    query = """
        SELECT
            sti.item_code,
            sti.item_name,
            sti.system_qty,
            sti.total_qty_counted AS inventory_qty,
            sti.difference,
            sti.tag,
            sti.remarks,
            IFNULL(bin.valuation_rate, 0) AS cost
        FROM `tabStock Taking Summary` sts
        INNER JOIN `tabStock Taking Summary Item` sti
            ON sti.parent = sts.name
        LEFT JOIN `tabBin` bin
            ON bin.item_code = sti.item_code
            AND bin.warehouse = sts.warehouse
        WHERE
            sts.name = %(summary)s
            AND sti.difference != 0
            AND sti.tag IS NOT NULL
        ORDER BY sti.tag, sti.item_code
    """

    rows = frappe.db.sql(query, {"summary": filters["stock_taking_summary"]}, as_dict=True)

    data = []
    current_tag = None
    sno = 0

    for row in rows:
        # Logical grouping header (no page break here)
        if current_tag != row.tag:
            data.append({
                "item_code": f"=== {row.tag} ITEMS ===",
            })
            current_tag = row.tag
            sno = 0

        sno += 1
        diff_value = flt(row.difference) * flt(row.cost)

        remarks = "Excess Stock" if row.tag == "E" else "Shortage Stock"

        data.append({
            "sno": sno,
            "item_code": row.item_code,
            "item_name": row.item_name,
            "system_qty": row.system_qty,
            "inventory_qty": row.inventory_qty,
            "difference": row.difference,
            "cost": row.cost,
            "diff_value": diff_value,
            "remarks": row.remarks,
            "tag": row.tag,
        })

    return data
