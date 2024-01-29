import frappe
# frappe.init(site="hoda-dev.erpgulf.com")
# frappe.connect()
import sys
from frappe import _

@frappe.whitelist(allow_guest=True)
def validate_returned_quantity(doc_name):
    try:
        # Get the Delivery Note document
        doc = frappe.get_doc('Delivery Note', doc_name)

        # Initialize dictionary to store differences for each item
        differences = {}

        # Validate quantity for each item
        for item in doc.items:
            difference = validate_item_quantity(item, doc)
            differences[item.name] = difference
        has_zero_difference = any(difference == 0 for difference in differences.values())

        if has_zero_difference:
            # Set the document status to 'Closed'
            frappe.db.set_value('Delivery Note', doc_name, 'status', 'Closed')
        return differences
    except Exception as e:
        # Log or handle the exception appropriately
        frappe.msgprint(str(e))

# Function to validate quantity for each item
def validate_item_quantity(item, delivery_note_doc):
    original_qty = abs(item.get('qty', 0))
    returned_qty = abs(item.get('returned_qty', 0))
    sales_invoice_return_qty = 0
    # frappe.msgprint(f"Original Qty: {original_qty}, Returned Qty: {returned_qty}")
    # Get Sales Invoice linked to the Delivery Note item
    sales_invoice_name = frappe.get_value('Sales Invoice Item', {'delivery_note': delivery_note_doc.name}, 'parent')
    qty_in_invoice = 0

    if sales_invoice_name:
        # Get Sales Invoice document
        sales_invoice_doc = frappe.get_doc('Sales Invoice', sales_invoice_name)

        # Calculate total returned quantity in Sales Invoice
        for invoice_item in sales_invoice_doc.items:
            sales_invoice_return_qty = abs(invoice_item.get('qty', 0))
            # frappe.msgprint(f"Returned Quantity for Item {item.item_code}: {sales_invoice_return_qty}")
        # Get the original Sales Invoice linked to the current Sales Invoice
        original_sales_invoice_note = sales_invoice_doc.get('return_against')
        if original_sales_invoice_note:
            original_sales_invoice_doc = frappe.get_doc('Sales Invoice', original_sales_invoice_note)

            # Calculate total quantity in the original Sales Invoice
            for invoice_item in original_sales_invoice_doc.items:
                qty_in_invoice = invoice_item.get('qty', 0)
                # frappe.msgprint(f"Quantity in Sales Invoice for item {invoice_item.item_code}: {qty_in_invoice}")
    else:
        # Handle the case where no Sales Invoice is linked
        pass
                  
    # Calculate the difference and set it in the item
    difference = ((original_qty - returned_qty) + sales_invoice_return_qty) - qty_in_invoice
    item.difference = difference

    return difference