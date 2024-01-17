// Copyright (c) 2023, Erpgulf and contributors
// For license information, please see license.txt

frappe.query_reports["Sales By Branch Summary"] = {
	"filters": [
		{
			"fieldname":"year",
			"label":"Year",
			"fieldtype":"Select",
			"options":['2024','2023','2022'],
			"default":'2024',
			"width":"100",
			"reqd":0,
		}

	]
};
