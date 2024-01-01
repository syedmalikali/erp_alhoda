import frappe
@frappe.whitelist()
def get_last_item():
	return frappe.get_all("Item", limit_page_length = 1)[0]
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

