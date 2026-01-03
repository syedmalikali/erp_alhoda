import frappe
from frappe.utils import nowdate, add_months
import uuid

@frappe.whitelist()
def test(item_code):

	# --- 1. CONFIG ---
	expiry_months = 12            # months after manufacture
	posting_time = "12:00:00"     # time for stock reconciliation

	# --- 2. Fetch current stock per warehouse ---
	bins = frappe.db.sql("""
		SELECT warehouse, actual_qty, valuation_rate
		FROM `tabBin`
		WHERE item_code=%s AND actual_qty != 0
	""", (item_code,), as_dict=True)

	if not bins:
		frappe.throw(f"No stock found for item {item_code}")

	# Save stock in array for later
	stock_array = []
	for b in bins:
		stock_array.append({
			"warehouse": b['warehouse'],
			"qty": b['actual_qty'],
			"valuation_rate": b['valuation_rate'] or 0
		})

	# --- 3. Make existing stock zero via Stock Reconciliation ---
	zero_items = []
	for s in stock_array:
		zero_items.append({
			"item_code": item_code,
			"warehouse": s['warehouse'],
			"qty": 0,  # negative to zero out
			"valuation_rate": s['valuation_rate'],
		})

	sr_zero = frappe.get_doc({
		"doctype": "Stock Reconciliation",
		"posting_date": nowdate(),
		"posting_time": posting_time,
		"items": zero_items,
		"purpose": "Stock Reconciliation"
	})
	sr_zero.insert()
	sr_zero.submit()
	frappe.db.commit()
	print("✔ Existing stock zeroed out successfully!")

	# --- 4. Enable batch and expiry via SQL ---
	frappe.db.sql(f"""
		UPDATE `tabItem`
		SET has_batch_no = 1,
			has_expiry_date = 1
		WHERE name = %s
	""", (item_code,))
	frappe.db.commit()
	print(f"✔ Enabled batch and expiry for item {item_code}")

	# --- 5. Create new Batch via SQL ---
	batch_id = "BATCH-CPS"
	manufacture_date = nowdate()
	expiry_date = add_months(manufacture_date, expiry_months)
	batch = frappe.get_doc({
		"doctype": "Batch",
		"batch_id": batch_id,
		"item": item_code,
		"manufacturing_date": manufacture_date,
		"expiry_date": expiry_date
	})
	batch.insert()
	frappe.db.commit()
	print("Created Batch:", batch_id, "Expiry:", expiry_date)

	# --- 6. Prepare Stock Reconciliation items with batch ---
	sr_items = []
	for s in stock_array:
		sr_items.append({
			"item_code": item_code,
			"warehouse": s['warehouse'],
			"qty": s['qty'],
			"use_serial_batch_fields":1,
			"valuation_rate": s['valuation_rate'],
			"batch_no": 'BATCH-CPS'
		})

	sr_add = frappe.get_doc({
		"doctype": "Stock Reconciliation",
		"posting_date": nowdate(),
		"posting_time": posting_time,
		"items": sr_items,
		"purpose": "Stock Reconciliation"
	})
	sr_add.insert()
	sr_add.submit()
	frappe.db.commit()
	print(f"✔ Stock migrated to batch {batch_id} successfully!")
	return


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



