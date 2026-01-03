import frappe
from frappe.utils import flt, getdate, add_months

def execute(filters=None):
    if not filters:
        return [], []

    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(filters, data)

    # return summary HTML in ERPNext v15 format
    return columns, data, None, None, summary


def get_columns():
    return [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 220},
        {"label": "No. of Visits", "fieldname": "visit_count", "fieldtype": "Int", "width": 120},
        {"label": "Invoice Value (Current Month)", "fieldname": "invoice_value", "fieldtype": "Currency", "width": 180},
        {"label": "Receivables <30 Days", "fieldname": "receivables_30", "fieldtype": "Currency", "width": 150},
        {"label": "Receivables 30-60 Days", "fieldname": "receivables_60", "fieldtype": "Currency", "width": 150},
        {"label": "Receivables 60-90 Days", "fieldname": "receivables_90", "fieldtype": "Currency", "width": 150},
        {"label": "Receivables >90 Days", "fieldname": "receivables_120", "fieldtype": "Currency", "width": 150},
        {"label": "Total Receivables", "fieldname": "total_receivables", "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    invoices = frappe.db.sql("""
        SELECT 
            si.customer,
            SUM(si.grand_total) AS invoice_value,
            COUNT(si.name) AS visit_count
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
        AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY si.customer
    """, filters, as_dict=True)

    data = []
    for inv in invoices:
        receivables = frappe.db.sql("""
            SELECT
                SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) <= 30 THEN outstanding_amount ELSE 0 END) AS r30,
                SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) BETWEEN 31 AND 60 THEN outstanding_amount ELSE 0 END) AS r60,
                SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) BETWEEN 61 AND 90 THEN outstanding_amount ELSE 0 END) AS r90,
                SUM(CASE WHEN DATEDIFF(CURDATE(), posting_date) > 90 THEN outstanding_amount ELSE 0 END) AS r120
            FROM `tabSales Invoice`
            WHERE customer = %(customer)s AND docstatus = 1
        """, {"customer": inv.customer}, as_dict=True)[0]

        total = flt(receivables.r30) + flt(receivables.r60) + flt(receivables.r90) + flt(receivables.r120)

        data.append({
            "customer": inv.customer,
            "visit_count": inv.visit_count,
            "invoice_value": inv.invoice_value,
            "receivables_30": receivables.r30,
            "receivables_60": receivables.r60,
            "receivables_90": receivables.r90,
            "receivables_120": receivables.r120,
            "total_receivables": total
        })

    return data


def get_summary(filters, data):
    employee_name, sector = "", ""

    if filters.get("employee"):
        emp = frappe.db.get_value("Employee", filters.employee, ["employee_name", "department"], as_dict=True)
        if emp:
            employee_name = emp.employee_name
            sector = emp.department

    # Calculate totals
    total_existing = sum([d["invoice_value"] for d in data])
    total_receivables = sum([d["total_receivables"] for d in data])

    html = f"""
        <div style="margin-bottom:10px">
            <h4><b>Monthly Sales Summary</b></h4>
            <table class="table table-bordered" style="width:60%">
                <tr>
                    <td><b>Employee</b></td><td>{employee_name or '-'}</td>
                    <td><b>Sector</b></td><td>{sector or filters.get('sector') or '-'}</td>
                </tr>
                <tr>
                    <td><b>From Date</b></td><td>{filters.get('from_date')}</td>
                    <td><b>To Date</b></td><td>{filters.get('to_date')}</td>
                </tr>
                <tr>
                    <td><b>Total Customers</b></td><td>{len(data)}</td>
                    <td><b>Total Receivables</b></td><td>{frappe.utils.fmt_money(total_receivables)}</td>
                </tr>
                <tr>
                    <td><b>Total Sales Value</b></td><td colspan="3">{frappe.utils.fmt_money(total_existing)}</td>
                </tr>
            </table>
        </div>
    """

    return [{"type": "html", "value": html}]
