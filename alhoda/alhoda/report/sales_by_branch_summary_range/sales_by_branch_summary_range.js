// Copyright (c) 2025, Erpgulf and contributors
// For license information, please see license.txt

frappe.query_reports["Sales By Branch Summary Range"] = {
    filters: [
        {
            fieldname: "date_range",
            label: __("Date Range"),
            fieldtype: "Select",
			options: [
				"Last Week",
				"Last Month",
				"Last Quarter",
				"Last 6 months",
				"Last Year",
				"This Week",
				"This Month",
				"This Quarter",
				"This Year",
			],
	    default: "This Year",
            reqd: 1,
            
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            depends_on: "eval:doc.date_range === 'custom'"
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            depends_on: "eval:doc.date_range === 'custom'"
        }
    ]
};
