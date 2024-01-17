// Copyright (c) 2024, Erpgulf and contributors
// For license information, please see license.txt

frappe.query_reports["Alhoda Price History S"] = {
	"filters": [
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
                        "reqd":1,
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Data",
                        "reqd":0,
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
