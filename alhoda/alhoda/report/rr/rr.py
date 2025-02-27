import frappe
from frappe import _

def get_columns():
    return [
        {'fieldname': 'item_tax_template', 'label': _('Title'), 'fieldtype': 'Data', 'width': 200},
        {'fieldname': 'InvNetTotal', 'label': _('Amount'), 'fieldtype': 'Currency', 'width': 150},
        {'fieldname': 'CrnNetTotal', 'label': _('Adjustment'), 'fieldtype': 'Currency', 'width': 150},
        {'fieldname': 'Tax', 'label': _('VAT Amount'), 'fieldtype': 'Currency', 'width': 150}
    ]

def get_data(filters=None):
    if not filters:
        filters = {}

    company = filters.get('company')
    dt_from = filters.get('dt_from')
    dt_to = filters.get('dt_to')

    if not (company and dt_from and dt_to):
        frappe.throw(_("Please provide valid Company, Date From, and Date To values."))

    base_query = """
        SELECT 
            kvsa.parent AS item_tax_template,
            kvsa.tax_type AS account,
            COALESCE(SUM(CASE WHEN si.is_return = 0 THEN si.net_total ELSE 0 END), 0) AS InvNetTotal,
            COALESCE(SUM(CASE WHEN si.is_return = 1 THEN si.net_total ELSE 0 END), 0) AS CrnNetTotal,
            COALESCE(SUM(stc.total), 0) AS Total,
            COALESCE(SUM(stc.tax_amount_after_discount_amount), 0) AS Tax
        FROM 
            `tabItem Tax Template Detail` kvsa
        LEFT JOIN 
            {tax_table} stc ON stc.account_head = kvsa.tax_type
        LEFT JOIN 
            {invoice_table} si ON si.name = stc.parent 
            AND si.posting_date BETWEEN %(dt_from)s AND %(dt_to)s 
            AND si.docstatus = 1 
            AND si.company = %(company)s
        GROUP BY 
            kvsa.parent, kvsa.tax_type
    """

    vat_on_sales = frappe.db.sql(base_query.format(tax_table="`tabSales Taxes and Charges`", invoice_table="`tabSales Invoice`"), 
                                 {'company': company, 'dt_from': dt_from, 'dt_to': dt_to}, as_dict=True)
    vat_on_purchases = frappe.db.sql(base_query.format(tax_table="`tabPurchase Taxes and Charges`", invoice_table="`tabPurchase Invoice`"), 
                                     {'company': company, 'dt_from': dt_from, 'dt_to': dt_to}, as_dict=True)

    # Combine results with header and footer rows
    data = [
        {'item_tax_template': 'VAT on Sales', 'account': '', 'InvNetTotal': None, 'CrnNetTotal': None, 'Tax': None}
    ] + vat_on_sales + [
        {'item_tax_template': 'Total', 'account': '', 
         'InvNetTotal': sum(d['InvNetTotal'] for d in vat_on_sales), 
         'CrnNetTotal': sum(d['CrnNetTotal'] for d in vat_on_sales), 
         'Tax': sum(d['Tax'] for d in vat_on_sales)}
    ] + [
        {'item_tax_template': '', 'account': '', 'InvNetTotal': None, 'CrnNetTotal': None, 'Tax': None},
        {'item_tax_template': 'VAT on Purchase', 'account': '', 'InvNetTotal': None, 'CrnNetTotal': None, 'Tax': None}
    ] + vat_on_purchases + [
        {'item_tax_template': 'Total', 'account': '', 
         'InvNetTotal': sum(d['InvNetTotal'] for d in vat_on_purchases), 
         'CrnNetTotal': sum(d['CrnNetTotal'] for d in vat_on_purchases), 
         'Tax': sum(d['Tax'] for d in vat_on_purchases)}
    ]

    return data

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data
