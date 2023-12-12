// Copyright (c) 2023, Erpgulf and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Wise Sales Price"] = {
	"filters": [
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
                        "reqd":1,
		},
		{
			"fieldname":"item_code",
			"label":"Item Code",
			"fieldtype":"Data",
			"Default":"AB",
			"width":"100",
			"reqd":0,
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},


	]
};
