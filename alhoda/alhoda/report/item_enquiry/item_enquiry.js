// Copyright (c) 2023, Erpgulf and contributors
// For license information, please see license.txt

frappe.query_reports["Item Enquiry"] = {
	"filters": [
		{
			"fieldname":"item_code",
			"label":"Item Code",
			"fieldtype":"Data",
			"width":"100",

		},
		{
			"fieldname":"description",
			"label":"Description",
			"fieldtype":"Data",
			"Default":"AB",
			"width":"150",
			
		},

		{
			"fieldname":"hide_zero_qty",
			"label":"Hide Zero Qty",
			"fieldtype":"Check",
			"default":1,

		},

	]
};
