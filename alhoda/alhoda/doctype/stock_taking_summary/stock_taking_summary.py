# Copyright (c) 2025, Syedmalikali and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate
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

        # Fetch system items from Bin
        system_items = frappe.get_all(
            "Bin",
            filters={"warehouse": self.warehouse},
            fields=["item_code"]
        )
        all_item_codes = set(d.item_code for d in system_items)

        # Fetch Stock Taking Entries
        entries = frappe.get_all(
            "Stock Taking Entry",
            filters={"inventory_identifier": self.inventory_identifier},
            fields=["item_code", "inventory_qty", "page_number", "inventory_date"]
        )

        for entry in entries:
            all_item_codes.add(entry.item_code)

        if not all_item_codes:
            frappe.msgprint("No items found in system or entries.")
            return

        entry_map = {}
        inventory_date_map = {}

        default_inventory_date = (
            max([d.inventory_date for d in entries])
            if entries else frappe.utils.nowdate()
        )

        for entry in entries:
            item_code = entry.item_code
            if item_code not in entry_map:
                entry_map[item_code] = {
                    "total_qty": 0.0,
                    "pages": {}
                }
                inventory_date_map[item_code] = entry.inventory_date

            entry_map[item_code]["total_qty"] += flt(entry.inventory_qty)

            page_num = entry.page_number or "Unspecified"
            entry_map[item_code]["pages"].setdefault(page_num, 0.0)
            entry_map[item_code]["pages"][page_num] += flt(entry.inventory_qty)

        summary_items = []

        for item_code in all_item_codes:
            data = entry_map.get(item_code, {"total_qty": 0.0, "pages": {}})
            inv_date = inventory_date_map.get(item_code, default_inventory_date)

            system_qty = get_stock_balance(
                item_code,
                self.warehouse,
                inv_date
            )

            page_desc_parts = []

            def sort_key(k):
                return int(k) if str(k).isdigit() else 999999

            for page in sorted(data["pages"].keys(), key=sort_key):
                qty = data["pages"][page]
                page_desc_parts.append(
                    f"{page}-{int(qty) if qty % 1 == 0 else qty}"
                )

            page_desc = ", ".join(page_desc_parts)

            f_date = getdate(self.from_date).strftime('%Y-%m-%d')
            t_date = getdate(self.to_date).strftime('%Y-%m-%d')

            movement_url = (
                f"/app/query-report/Stock Ledger?"
                f"item_code={item_code}&warehouse={self.warehouse}"
                f"&from_date={f_date}&to_date={t_date}"
            )
            movement_link = f"<a href='{movement_url}' target='_blank'>Check Movement</a>"

            difference = flt(data["total_qty"]) - flt(system_qty)
            if difference == 0:
                continue

            summary_items.append({
                "item_code": item_code,
                "item_name": frappe.db.get_value("Item", item_code, "item_name"),
                "total_qty_counted": data["total_qty"],
                "corrected_qty": system_qty,
                "system_qty": system_qty,
                "difference": difference,
                "qty_description_by_page": page_desc,
                "check_movement": movement_link
            })

        summary_items.sort(key=lambda x: x["item_code"])

        self.set("items", summary_items)
        self.save()
        frappe.msgprint(f"Summary generated with {len(self.items)} items.")

    # -----------------------------------
    # ADJUSTMENT ENTRY (CALLED FROM CLIENT)
    # -----------------------------------
    @frappe.whitelist()
    def make_adjustment_entry(self, item_code, adjustment_qty):
        adjustment_qty = flt(adjustment_qty)

        if adjustment_qty == 0:
            return

        # Delete any existing adjustment entries for this item on page 200
        frappe.db.delete(
            "Stock Taking Entry",
            filters={
                "inventory_identifier": self.inventory_identifier,
                "item_code": item_code,
                "page_number": 200
            }
        )

        # Insert new adjustment entry
        frappe.get_doc({
            "doctype": "Stock Taking Entry",
            "inventory_identifier": self.inventory_identifier,
            "inventory_date": nowdate(),
            "warehouse": self.warehouse,
            "item_code": item_code,
            "inventory_qty": adjustment_qty,
            "page_number": 200,
            "counted_by": frappe.session.user
        }).insert(ignore_permissions=True)

        frappe.db.commit()
