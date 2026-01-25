import frappe
from frappe.utils import nowdate, add_months
import uuid



def get_last_item():
	items = frappe.get_all("Item", limit_page_length = 1)
	return items[0] if items else None
def get_doqty(item_code):
    conditions = " and item_code = '%s'" % item_code
    return frappe.db.sql("""
        SELECT
              dnt.parent,dnt.item_code,
              dnt.qty - COALESCE(dnt.returned_qty, 0) AS do_qty,
              COALESCE((SELECT SUM(qty * -1)
        FROM `tabSales Invoice Item` WHERE dn_detail = dnt.name ), 0) AS inv_qty
        FROM
             `tabDelivery Note Item` dnt where qty>0 and docstatus=1;
        """ %
        conditions, as_dict=1)
@frappe.whitelist()
def check_draft_invoices(delivery_note):
    draft_invoices = frappe.db.sql("""
        SELECT si.name
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE si.docstatus = 0
        AND sii.delivery_note = %s
    """, (delivery_note,), as_dict=True)

    return draft_invoices
@frappe.whitelist()
def download_html(
	doctype: str,
	name: str,
	format=None,
	doc=None,
	no_letterhead=0,
	language=None,
	letterhead=None,
):
	doc = doc or frappe.get_doc(doctype, name)
	validate_print_permission(doc)
	with print_language(language):
		html_content = frappe.get_print(
			doctype,
			name,
			format,
			doc=doc,
			as_pdf=False,  # This is the key change
			letterhead=letterhead,
			no_letterhead=no_letterhead,
		)
	frappe.local.response.filename = "{name}.html".format(name=name.replace(" ", "-").replace("/", "-"))
	frappe.local.response.filecontent = html_content
	frappe.local.response.type = "html"



