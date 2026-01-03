# In your custom_app/custom_app/report/item_wise_cogs_reconciliation/item_wise_cogs_reconciliation.py

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    # Define the columns as per the table above
    return [
        {"fieldname": "item_code", "label": _("Item Code"), "fieldtype": "Link", "options": "Item", "width": 120},
        {"fieldname": "item_name", "label": _("Item Name"), "fieldtype": "Data", "width": 180},
        {"fieldname": "opening_qty", "label": _("Opening Qty"), "fieldtype": "Float", "width": 100},
        {"fieldname": "opening_value", "label": _("Opening Value"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "pr_qty", "label": _("PR Qty"), "fieldtype": "Float", "width": 100},
        {"fieldname": "pr_value", "label": _("PR Value"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "landed_cost_value", "label": _("Landed Cost"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "total_in_qty", "label": _("Total In Qty"), "fieldtype": "Float", "width": 120},
        {"fieldname": "total_in_value", "label": _("Total In Value"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "sales_qty", "label": _("Sales Qty"), "fieldtype": "Float", "width": 100},
        {"fieldname": "cogs_value", "label": _("COGS Value"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "transfer_out_qty", "label": _("Transfer Out Qty"), "fieldtype": "Float", "width": 120},
        {"fieldname": "transfer_out_value", "label": _("Transfer Out Value"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "mfg_consumption_qty", "label": _("Mfg Consume Qty"), "fieldtype": "Float", "width": 120},
        {"fieldname": "mfg_consumption_value", "label": _("Mfg Consume Value"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "closing_qty", "label": _("Closing Qty"), "fieldtype": "Float", "width": 100},
        {"fieldname": "closing_value", "label": _("Closing Value"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "gl_cogs_value", "label": _("GL COGS"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "gl_inventory_change", "label": _("GL Inv Change"), "fieldtype": "Currency", "width": 140},
        {"fieldname": "cogs_variance", "label": _("COGS Variance"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "stock_variance", "label": _("Stock Variance"), "fieldtype": "Currency", "width": 120},
    ]

def get_data(filters):
    company = filters.get("company")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    item_group = filters.get("item_group")
    item_code_filter = filters.get("item_code")
    warehouse_filter = filters.get("warehouse") # Note: COGS is generally company-wide, not warehouse specific for financial reporting

    # Initialize a dictionary to store item-wise data
    item_data = {} # Key: item_code, Value: dictionary of metrics

    # --- 1. Get all relevant items ---
    conditions = []
    if item_group:
        conditions.append(f"item_group = '{item_group}'")
    if item_code_filter:
        conditions.append(f"name = '{item_code_filter}'")

    item_query = f"SELECT name, item_name FROM `tabItem` {'WHERE ' + ' AND '.join(conditions) if conditions else ''}"
    items = frappe.db.sql(item_query, as_dict=True)

    for item in items:
        item_data[item.name] = {
            "item_code": item.name,
            "item_name": item.item_name,
            "opening_qty": 0, "opening_value": 0,
            "pr_qty": 0, "pr_value": 0,
            "landed_cost_value": 0,
            "total_in_qty": 0, "total_in_value": 0,
            "sales_qty": 0, "cogs_value": 0,
            "transfer_out_qty": 0, "transfer_out_value": 0,
            "mfg_consumption_qty": 0, "mfg_consumption_value": 0,
            "closing_qty": 0, "closing_value": 0,
            "gl_cogs_value": 0, "gl_inventory_change": 0,
            "cogs_variance": 0, "stock_variance": 0
        }

    # --- 2. Calculate Opening Stock (before from_date) ---
    # Fetch Stock Ledger Entries before from_date to get opening balance
    # Sum actual_qty * valuation_rate for entries up to (from_date - 1 day)
    # This requires careful handling of valuation_rate as it changes
    # A simpler approach for opening stock is to use get_stock_balance_for_item
    # or sum SLEs before the period.
    # For accuracy, we will sum all SLEs up to (from_date - 1 day) for each item.

    # Example query for opening balance (can be optimized)
    sle_opening = frappe.db.sql(f"""
        SELECT
            item_code,
            SUM(actual_qty) as qty,
            SUM(actual_qty * valuation_rate) as value
        FROM `tabStock Ledger Entry`
        WHERE
            posting_date < '{from_date}' AND
            company = '{company}'
            {"AND item_code = '" + item_code_filter + "'" if item_code_filter else ""}
            {"AND warehouse = '" + warehouse_filter + "'" if warehouse_filter else ""}
        GROUP BY item_code
    """, as_dict=True)


    for entry in sle_opening:
        if entry.item_code in item_data:
            item_data[entry.item_code]["opening_qty"] = entry.qty
            item_data[entry.item_code]["opening_value"] = entry.value

    # --- 3. Process Stock Ledger Entries (SLEs) within the period ---
    # This is the most crucial part. We iterate through SLEs and classify them.
    # Adjust the query to include necessary fields for classification.

    sle_entries = frappe.db.sql(f"""
        SELECT
            item_code,
            posting_date,
            actual_qty,
            valuation_rate,
            stock_value, -- This is actual_qty * valuation_rate
            voucher_type,
            voucher_no,
            stock_entry_type, -- For Stock Entries
            is_cancelled
        FROM `tabStock Ledger Entry`
        WHERE
            posting_date >= '{from_date}' AND posting_date <= '{to_date}' AND
            company = '{company}' AND is_cancelled = 0
            {"AND item_code = '" + item_code_filter + "'" if item_code_filter else ""}
            {"AND warehouse = '" + warehouse_filter + "'" if warehouse_filter else ""}
        ORDER BY posting_date, creation
    """, as_dict=True)

    # Temporary store for current stock balance to calculate closing
    current_stock_balance = {item_code: {"qty": item_data[item_code]["opening_qty"], "value": item_data[item_code]["opening_value"]} for item_code in item_data}


    for entry in sle_entries:
        item_code = entry.item_code
        if item_code not in item_data:
            continue # Skip if not in our filtered items

        # Update current stock balance for closing calculation
        current_stock_balance[item_code]["qty"] += entry.actual_qty
        current_stock_balance[item_code]["value"] += entry.stock_value

        # Classify SLEs
        if entry.voucher_type == "Purchase Receipt":
            item_data[item_code]["pr_qty"] += entry.actual_qty
            item_data[item_code]["pr_value"] += entry.stock_value # This includes landed cost if applicable at PR stage

        elif entry.voucher_type == "Landed Cost Voucher":
            # Landed Cost Vouchers generate SLEs that *only* adjust valuation, actual_qty is usually 0
            # The stock_value represents the landed cost amount added.
            item_data[item_code]["landed_cost_value"] += entry.stock_value
            # Note: if "Set Landed Cost Based on Purchase Invoice Rate" is ON, this will be the adjustment post-PR

        elif entry.voucher_type == "Delivery Note":
            # Sales (COGS)
            item_data[item_code]["sales_qty"] += abs(entry.actual_qty) # actual_qty is negative for sales
            item_data[item_code]["cogs_value"] += abs(entry.stock_value) # stock_value is negative for sales

        elif entry.voucher_type == "Stock Entry":
            if entry.stock_entry_type == "Material Transfer":
                if entry.actual_qty < 0: # Outgoing transfer
                    item_data[item_code]["transfer_out_qty"] += abs(entry.actual_qty)
                    item_data[item_code]["transfer_out_value"] += abs(entry.stock_value)
                # Incoming transfers are like purchases for that warehouse/item, but don't add to company-wide "Purchases"

            elif entry.stock_entry_type == "Material Consumption":
                item_data[item_code]["mfg_consumption_qty"] += abs(entry.actual_qty) # actual_qty is negative
                item_data[item_code]["mfg_consumption_value"] += abs(entry.stock_value) # stock_value is negative

            # Add other Stock Entry types if needed (e.g., Material Issue, Repack, etc.)

        # Handle Purchase Invoice vs Purchase Receipt Rate Differences:
        # If "Set Landed Cost Based on Purchase Invoice Rate" is enabled,
        # ERPNext often creates an additional SLE with 0 actual_qty and a stock_value to adjust the item's valuation
        # when a Purchase Invoice is submitted at a different rate than its linked Purchase Receipt.
        # These are usually classified as "Purchase Receipt" voucher_type but have 0 qty and only a value.
        # We need to ensure we don't double count. The stock_value from PR SLEs *should* capture this,
        # but cross-verify that the `landed_cost_value` logic accounts for it without duplication.
        # A robust solution might involve:
        # 1. Summing `stock_value` from PRs where `actual_qty > 0` for `pr_value`.
        # 2. Summing `stock_value` from LCVs for `landed_cost_value`.
        # 3. Summing `stock_value` from PRs where `actual_qty = 0` (these are rate adjustments) and attribute
        #    them either to `landed_cost_value` or a separate `rate_adjustment_value` column for clarity.
        # For simplicity in this pseudo-code, `pr_value` and `landed_cost_value` will capture the relevant valuation changes.


    # --- 4. Calculate Closing Stock ---
    for item_code in item_data:
        item_data[item_code]["closing_qty"] = current_stock_balance[item_code]["qty"]
        item_data[item_code]["closing_value"] = current_stock_balance[item_code]["value"]
        
        # Calculate derived values
        item_data[item_code]["total_in_qty"] = item_data[item_code]["opening_qty"] + item_data[item_code]["pr_qty"]
        item_data[item_code]["total_in_value"] = item_data[item_code]["opening_value"] + item_data[item_code]["pr_value"] + item_data[item_code]["landed_cost_value"]


    # --- 5. Fetch GL Entries for Reconciliation ---
    # COGS (Expenses) and Inventory Asset (Asset) accounts
    gl_entries = frappe.db.sql(f"""
        SELECT
            gl.account,
            gl.item_code,
            SUM(gl.debit) as total_debit,
            SUM(gl.credit) as total_credit
        FROM `tabGL Entry` gl
        WHERE
            gl.posting_date >= '{from_date}' AND gl.posting_date <= '{to_date}' AND
            gl.company = '{company}' AND gl.is_cancelled = 0 AND gl.item_code IS NOT NULL
            {"AND gl.item_code = '" + item_code_filter + "'" if item_code_filter else ""}
        GROUP BY gl.account, gl.item_code
    """, as_dict=True)

    cogs_accounts = frappe.get_list("Account", filters={"account_type": "Cost of Goods Sold", "company": company}, pluck="name")
    inventory_asset_accounts = frappe.get_list("Account", filters={"account_type": "Stock", "company": company}, pluck="name")

    for entry in gl_entries:
        item_code = entry.item_code
        if item_code not in item_data:
            continue

        if entry.account in cogs_accounts:
            # COGS is typically debit (increase expense)
            item_data[item_code]["gl_cogs_value"] += (entry.debit - entry.credit)
        elif entry.account in inventory_asset_accounts:
            # Inventory asset increases with debit, decreases with credit
            item_data[item_code]["gl_inventory_change"] += (entry.debit - entry.credit)

    # --- 6. Calculate Variances ---
    # Final pass to calculate variances
    final_data = []
    for item_code, values in item_data.items():
        if not values["item_code"]: # Skip if item_code somehow got lost or empty
            continue

        values["cogs_variance"] = values["cogs_value"] - values["gl_cogs_value"]

        # Reconciling stock change:
        # Expected Net Change in Stock Value = (Purchases + Landed Cost) - (COGS + Transfers Out + Mfg Consumption)
        # Actual Net Change in Stock Value = Closing Stock Value - Opening Stock Value (from SLEs)
        # GL Inventory Change = Debit - Credit in Inventory Asset GL (from GL Entries)
        # For simplicity, let's compare:
        # (Opening + Inflows - Outflows) = Closing
        # (opening_value + pr_value + landed_cost_value) - (cogs_value + transfer_out_value + mfg_consumption_value) - closing_value
        # This should ideally be 0.
        
        calculated_net_stock_change = (values["pr_value"] + values["landed_cost_value"]) - \
                                      (values["cogs_value"] + values["transfer_out_value"] + values["mfg_consumption_value"])
        
        actual_sle_stock_change = values["closing_value"] - values["opening_value"]

        # Variance is the difference between what stock movements (SLEs) tell us happened vs. what GL entries show for inventory asset.
        values["stock_variance"] = actual_sle_stock_change - values["gl_inventory_change"]
        
        final_data.append(values)

    return final_data