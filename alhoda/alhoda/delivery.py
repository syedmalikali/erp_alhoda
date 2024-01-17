import frappe
# frappe.init(site="hoda-dev.erpgulf.com")
# frappe.connect()
import sys
from frappe import _

@frappe.whitelist(allow_guest=True)
def validate_returned_quantity(doc_name):
    try:
        doc = frappe.get_doc('Delivery Note', doc_name)
        print("doc is",doc)
        for item in doc.items:
            validate_item_quantity(item, doc)
    except Exception as e:
        frappe.msgprint(str(e))

def validate_item_quantity(item, delivery_note_doc):
    original_qty = abs(item.get('qty', 0)) 
    returned_qty = abs(item.get('returned_qty', 0))
    # print(f"Original Qty: {original_qty}, Returned Qty: {returned_qty}")
    sales_invoice_return_qty = 0
    
    sales_invoice_name = frappe.get_value('Sales Invoice Item', {'delivery_note': delivery_note_doc.name}, 'parent')
    # print(f"sales invoice name:{sales_invoice_name}")
    if sales_invoice_name:
        sales_invoice_doc = frappe.get_doc('Sales Invoice', sales_invoice_name)
        # print(f"sales invoice doc:{sales_invoice_doc}")
        for item in sales_invoice_doc.items:
            sales_invoice_return_qty = abs(item.get('qty', 0)) 

            # print(f"Returned Quantity for Item {item.item_code}: {sales_invoice_return_qty}")
        original_sales_invoice_note = sales_invoice_doc.get('return_against')
        # print(f"sales invoice name:s{original_sales_invoice_note}")
        if original_sales_invoice_note:
            original_sales_invoice_doc = frappe.get_doc('Sales Invoice', original_sales_invoice_note)
            frappe.msgprint(f"Original sales invoice doc is: {original_sales_invoice_doc}")
            for invoice_item in original_sales_invoice_doc.items:
                qty_in_invoice = invoice_item.qty 
                frappe.msgprint(f"Quantity in Sales Invoice for item {invoice_item.item_code}: {qty_in_invoice}")
        else:
            frappe.msgprint("No linked Sales Invoice found for the given Delivery Note.")
            pass
 
        difference = ((original_qty - returned_qty) + sales_invoice_return_qty) - qty_in_invoice
        # print(f"Difference: {difference}")

        # Set the difference in the item for further reference
        item.difference = difference

        if difference == 0:
            delivery_note_doc.db_set('status', 'Closed', commit = True,update_modified=True)
            frappe.throw(_("Sales Return cannot be created for already completed delivery note {0} .").format(delivery_note_doc.name))
            
