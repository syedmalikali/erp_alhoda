frappe.query_reports["rr"] = {
	"filters": [
				{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
				{
			fieldname: "dt_from",
			label: __("From"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},		

		{
			"fieldname": "dt_to",
			"label": __("To"),
			"fieldtype": "Date",
		    default: frappe.datetime.get_today(),
		}

		
	],
    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // Check if the 'item_tax_template' column has 'Total' as content
        if (data && (data.item_tax_template === 'Total' || data.item_tax_template === 'VAT on Sales' || data.item_tax_template === 'VAT on Purchase' )) {
            // Apply bold style to the entire row
            value = "<b>" + value + "</b>";
        }

        return value;
    },
};