import frappe
# frappe.init(site="hoda-dev.erpgulf.com")
# frappe.connect()


@frappe.whitelist(allow_guest=True)
def calculate_item_quantities(item_code):
    try:
      
        delivery_note_qty = frappe.get_all("Delivery Note Item", pluck="qty", filters={"name": item_code, "docstatus": 1})
        returned_delivery_qty = frappe.get_all("Delivery Note Item", pluck="qty", filters={"dn_detail": item_code, "docstatus": 1})
        invoice_qty = frappe.get_all("Sales Invoice Item", pluck="qty", filters={"dn_detail": item_code, "docstatus": 1})

        # Calculate total quantities
        total_delivery_note_qty = sum(delivery_note_qty)
        total_returned_deliverynote_qty = sum(returned_delivery_qty)
        total_invoice_qty = sum(invoice_qty)

        # Calculate result
        result = (total_delivery_note_qty + total_returned_deliverynote_qty ) - total_invoice_qty

        return {
            "doqty": total_delivery_note_qty,
            "retqty": total_returned_deliverynote_qty,
            "invqty": total_invoice_qty,
            "result": result
        }
    except Exception as e:
        # Handle exceptions here
        return {"error": str(e)}


