frappe.query_reports["P"] = {
    "filters": [
        {
            "fieldname": "posting_date",
            "label": ("Posting Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "due_date",
            "label": ("To Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group"
        }
    ]
};