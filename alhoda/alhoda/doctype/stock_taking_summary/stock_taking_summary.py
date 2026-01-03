# Copyright (c) 2025, Syedmalikali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate
from erpnext.stock.utils import get_stock_balance

class StockTakingSummary(Document):
	@frappe.whitelist()
	def calculate_summary(self):
		if not self.inventory_identifier:
			frappe.throw("Please enter an Inventory Identifier first.")
		if not self.warehouse:
			frappe.throw("Please select a Warehouse first.")

		# Clear existing items
		self.set("items", [])

		# 1. Fetch all items available in this warehouse (System Stock)
		# We use stock bin to find items that have some presence in this warehouse
		# Or should we fetch ALL items? Usually stock taking is for items in the warehouse.
		# Let's fetch Items that exist in the system stock for this warehouse OR are counted.
		
		# Fetch all items in the warehouse currently (Non-zero balance? Or just any bin?)
		# To get a comprehensive list, we should look at Bin for this warehouse.
		system_items = frappe.get_all("Bin", filters={"warehouse": self.warehouse}, fields=["item_code"])
		all_item_codes = set(d.item_code for d in system_items)
		
		# 2. Fetch matching Stock Taking Entries
		entries = frappe.get_all(
			"Stock Taking Entry",
			filters={"inventory_identifier": self.inventory_identifier},
			fields=["item_code", "inventory_qty", "page_number", "inventory_date", "warehouse"]
		)
		
		# Add counted items to the set (in case they are new or not in Bin yet somehow)
		for entry in entries:
			all_item_codes.add(entry.item_code)

		if not all_item_codes:
			frappe.msgprint("No items found in system or entries.")
			return

		# Group entries by Item Code
		entry_map = {}
		inventory_date_map = {} # item_code -> date (for system balance lookup)
		
		# Default date for system balance if no entry found (use today or logic?)
		# If items are not counted, we should ideally pick the date from OTHER entries of the same identifier?
		# Or just use today? User said "invnetory date depends on entry". 
		# If uncounted, let's assume the Max date from entries, or Today.
		default_inventory_date = max([d.inventory_date for d in entries]) if entries else frappe.utils.nowdate()

		for entry in entries:
			item_code = entry.item_code
			if item_code not in entry_map:
				entry_map[item_code] = {
					"total_qty": 0.0,
					"pages": {}, # page_number -> qty
				}
				inventory_date_map[item_code] = entry.inventory_date
			
			entry_map[item_code]["total_qty"] += flt(entry.inventory_qty)
			
			page_num = entry.page_number or "Unspecified"
			if page_num not in entry_map[item_code]["pages"]:
				entry_map[item_code]["pages"][page_num] = 0.0
			entry_map[item_code]["pages"][page_num] += flt(entry.inventory_qty)

		# 3. Populate Child Table
		summary_items = []
		
		for item_code in all_item_codes:
			# Get data from entries
			data = entry_map.get(item_code, {"total_qty": 0.0, "pages": {}})
			
			# Determine Inventory Date for this item (use specific entry date or fallback)
			inv_date = inventory_date_map.get(item_code, default_inventory_date)

			# Get System Qty
			system_qty = get_stock_balance(
				item_code,
				self.warehouse,
				inv_date
			)

			# Format Page Description
			page_desc_parts = []
			# Sort pages: Integers first, then strings
			def sort_key(k):
				return int(k) if str(k).isdigit() else 999999
				
			sorted_pages = sorted(data["pages"].keys(), key=sort_key)
			for page in sorted_pages:
				qty = data["pages"][page]
				# Format: "Page-Qty"
				page_desc_parts.append(f"{page}-{int(qty) if qty % 1 == 0 else qty}")
			
			page_desc = ", ".join(page_desc_parts)

			# Generate Link for Movement Check
			# We pass a simple URL. The client script can ensure it opens correctly or we use HTML field.
			# Using HTML field in Child Table is good.
			# Query Report URL expects standard params.
			
			# Clean dates for URL
			f_date = frappe.utils.getdate(self.from_date).strftime('%Y-%m-%d')
			t_date = frappe.utils.getdate(self.to_date).strftime('%Y-%m-%d')
			
			movement_url = f"/app/query-report/Stock Ledger?item_code={item_code}&warehouse={self.warehouse}&from_date={f_date}&to_date={t_date}"
			movement_link = f"<a href='{movement_url}' target='_blank'>Check Movement</a>"

			summary_items.append({
				"item_code": item_code,
				"item_name": frappe.db.get_value("Item", item_code, "item_name"),
				"total_qty_counted": data["total_qty"],
				"system_qty": system_qty,
				"difference": data["total_qty"] - system_qty,
				"qty_description_by_page": page_desc,
				"check_movement": movement_link
			})

		# Sort items by difference (descending) so variances are on top? Or Item Code?
		# Let's sort by Item Code for now, or Difference if variance is key.
		summary_items.sort(key=lambda x: x['item_code'])

		self.set("items", summary_items)
		self.save()
		frappe.msgprint(f"Summary generated with {len(self.items)} items.")
