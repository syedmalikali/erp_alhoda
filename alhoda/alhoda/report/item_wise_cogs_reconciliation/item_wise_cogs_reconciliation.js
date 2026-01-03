// Copyright (c) 2025, Erpgulf and contributors
// For license information, please see license.txt

frappe.query_reports["Item-Wise COGS Reconciliation"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			// Sets the default 'From Date' to the start of the current fiscal year
			"default": frappe.datetime.get_fiscal_year(frappe.datetime.get_today(), true)[1]
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			// Sets the default 'To Date' to today
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			// This is a good practice: it filters the warehouse list based on the selected company
			"get_query": function() {
				var company = frappe.query_report.get_filter_value('company');
				if (!company) {
					frappe.throw(__("Please select a Company first"));
				}
				return {
					"doctype": "Warehouse",
					"filters": {
						"company": company
					}
				}
			}
		}
	]
};