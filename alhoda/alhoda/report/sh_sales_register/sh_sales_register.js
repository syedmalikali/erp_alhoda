frappe.query_reports["SH Sales Register"] = {
    "filters": frappe.query_reports["Sales Register"].filters.concat([
        // Add new filters
        {
            "fieldname": "custom_filter",
            "label": __("Custom Filter"),
            "fieldtype": "Data"
        }
    ])
};