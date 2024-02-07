import frappe
frappe.init(site="hoda-dev.erpgulf.com")
frappe.connect()
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
    sales_invoice_qty = 0
    # print(f"Original Qty: {original_qty}, Returned Qty: {returned_qty}")
    # Get Sales Invoice linked to the Delivery Note item
    sales_invoice_name = frappe.get_value('Sales Invoice Item', {'delivery_note': delivery_note_doc.name}, 'parent')
    # print(f"SIN{sales_invoice_name}")
    return_invoice_qty = 0

    if sales_invoice_name:
        # Get Sales Invoice document
        sales_invoice_doc = frappe.get_doc('Sales Invoice', sales_invoice_name)
        # print(f"SID{sales_invoice_doc}")
        # Calculate total returned quantity in Sales Invoice
        for invoice_item in sales_invoice_doc.items:
            sales_invoice_qty = abs(invoice_item.get('qty', 0))
            # print(f"Returned Quantity for Item {item.item_code}: {sales_invoice_qty}")
        # Get the original Sales Invoice linked to the current Sales Invoice
        original_sales_invoice_note = sales_invoice_doc.get('return_against')
        # print(f"OSIN{original_sales_invoice_note}")
        if original_sales_invoice_note:
            original_sales_invoice_doc = frappe.get_doc('Sales Invoice', original_sales_invoice_note)
            # print(f" ORIGISI DOC{original_sales_invoice_doc}")
            # Calculate total quantity in the original Sales Invoice
            for invoice_item in original_sales_invoice_doc.items:
                return_invoice_qty = invoice_item.get('qty', 0)
                # print(f"Quantity in Sales Invoice for item {invoice_item.item_code}: {return_invoice_qty}")
                
            # Calculate the difference when original sales invoice exists
            difference = ((original_qty - returned_qty) + sales_invoice_qty) - return_invoice_qty
        else:
            # Calculate the difference when no original sales invoice exists
            difference = ((original_qty - returned_qty) + return_invoice_qty) - sales_invoice_qty
    else:
        # Handle the case where no Sales Invoice is linked
        difference = original_qty - returned_qty
    # print(difference)
    # Set the difference in the item
    item.difference = difference
    # print(difference)

    return difference





def validate_sales_invoice_before_save(sales_invoice_doc):
    if not isinstance(sales_invoice_doc, dict):
        sales_invoice_doc = frappe.get_doc('Sales Invoice', sales_invoice_doc)
        print(sales_invoice_doc)
    for item in sales_invoice_doc.items:
        original_qty = 0
        
        # Retrieve the delivery note linked to the item
        delivery_note_name = item.delivery_note
        print(delivery_note_name)
        if delivery_note_name:
            # Get the delivery note document
            delivery_note_doc = frappe.get_doc('Delivery Note', delivery_note_name)
            
            # Retrieve the quantity from the delivery note
            qty = delivery_note_doc.get('qty')
            if qty is not None:
                original_qty = abs(qty)
            else:
                # Handle the case where qty is None or not present
                original_qty = 0
            
            # You can perform further validation or calculations here based on original_qty
            
            # For demonstration purposes, let's print the original quantity
            print(f"Original Quantity for item {item.item_code}: {original_qty}")
        else:
            frappe.throw(f"No Delivery Note found for item {item.item_code}.")        

validate_sales_invoice_before_save('KSI-24-00080')