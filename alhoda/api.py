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



@frappe.whitelist()
def get_invoice_preview(name):

    invoice = frappe.get_doc("Sales Invoice", name)

    items = frappe.get_all(
        "Sales Invoice Item",
        filters={"parent": name},
        fields=["item_name","qty","rate","amount"]
    )

    gl_entries = frappe.get_all(
        "GL Entry",
        filters={
            "voucher_no": name,
            "voucher_type": "Sales Invoice"
        },
        fields=["account","debit","credit","remarks"]
    )

    return {
        "name": invoice.name,
        "customer": invoice.customer,
        "status": invoice.status,
        "posting_date": invoice.posting_date,
        "due_date": invoice.due_date,
        "grand_total": invoice.grand_total,
        "items": items,
        "gl_entries": gl_entries
    }
# Server Script (API type) - rename to e.g. get_document_preview
@frappe.whitelist()
def get_document_preview():
    dt = frappe.form_dict.get("doctype")
    name = frappe.form_dict.get("name")

    if not dt or not name:
        frappe.throw("Doctype and Name required")

    doc = frappe.get_doc(dt, name)

    items = []
    if frappe.get_meta(dt).has_field("items"):
        items = frappe.get_all(
            f"{dt} Item",
            filters={"parent": name},
            fields=["item_name", "qty", "rate", "amount"]
        )

    gl_entries = frappe.get_all(
        "GL Entry",
        filters={"voucher_type": dt, "voucher_no": name},
        fields=["account", "debit", "credit", "remarks"]
    )

    return {
        "name": doc.name,
        "customer": doc.get("customer"),           # fallback if no customer
        "supplier": doc.get("supplier"),
        "party_name": doc.get("party_name"),
        "posting_date": doc.posting_date,
        "due_date": doc.get("due_date"),
        "grand_total": doc.get("grand_total") or doc.get("total") or doc.get("rounded_total") or 0,
        "status": doc.status,
        "currency": doc.currency or "INR",
        "items": items,
        "gl_entries": gl_entries
    }