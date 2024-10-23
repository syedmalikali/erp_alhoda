// Copyright (c) 2024, Erpgulf and contributors
// For license information, please see license.txt

frappe.query_reports["Alhoda Customer Aging Report"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "report_date",
			label: __("Posting Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "ageing_based_on",
			label: __("Ageing Based On"),
			fieldtype: "Select",
			options: "Posting Date\nDue Date",
			default: "Due Date",
		},
		{
			fieldname: "range1",
			label: __("Ageing Range 1"),
			fieldtype: "Int",
			default: "30",
			reqd: 1,
		},
		{
			fieldname: "range2",
			label: __("Ageing Range 2"),
			fieldtype: "Int",
			default: "60",
			reqd: 1,
		},
		{
			fieldname: "range3",
			label: __("Ageing Range 3"),
			fieldtype: "Int",
			default: "90",
			reqd: 1,
		},
		{
			fieldname: "range4",
			label: __("Ageing Range 4"),
			fieldtype: "Int",
			default: "120",
			reqd: 1,
		},
		{
			fieldname: "finance_book",
			label: __("Finance Book"),
			fieldtype: "Link",
			options: "Finance Book",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						company: company,
					},
				};
			},
		},
		{
			fieldname: "party_type",
			label: __("Party Type"),
			fieldtype: "Autocomplete",
			options: get_party_type_options(),
			on_change: function () {
				frappe.query_report.set_filter_value("party", "");
				frappe.query_report.toggle_filter_display(
					"customer_group",
					frappe.query_report.get_filter_value("party_type") !== "Customer"
				);
			},
		},
		{
			fieldname: "party",
			label: __("Party"),
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				if (!frappe.query_report.filters) return;

				let party_type = frappe.query_report.get_filter_value("party_type");
				if (!party_type) return;

				return frappe.db.get_link_options(party_type, txt);
			},
		},
		{
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "Link",
			options: "Customer Group",
		},
		{
			fieldname: "payment_terms_template",
			label: __("Payment Terms Template"),
			fieldtype: "Link",
			options: "Payment Terms Template",
		},
		{
			fieldname: "territory",
			label: __("Territory"),
			fieldtype: "Link",
			options: "Territory",
		},
		{
			fieldname: "sales_partner",
			label: __("Sales Partner"),
			fieldtype: "Link",
			options: "Sales Partner",
		},
		{
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			options: "Sales Person",
		},
		{
			fieldname: "based_on_payment_terms",
			label: __("Based On Payment Terms"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_future_payments",
			label: __("Show Future Payments"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_gl_balance",
			label: __("Show GL Balance"),
			fieldtype: "Check",
		},
		{
			fieldname: "for_revaluation_journals",
			label: __("Revaluation Journals"),
			fieldtype: "Check",
		},
	],

formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);
    console.log(data)
    // Accessing the value in the 14th column (index 13)
    let above120days = parseFloat(row[8].content || 0);
    let days120 = parseFloat(row[7].content || 0);
    let days90 = parseFloat(row[6].content || 0);
    let days60 = parseFloat(row[5].content || 0);
    let days30 = parseFloat(row[4].content || 0);

        
     if ((column.colIndex === 1 || column.colIndex === 8) && above120days > 0) { 
        // If the value in the 14th column is greater than 0, apply green highlight
        value = `<div style="background-color: #ff9fae; padding: 2px;">${value}</div>`;
    } else if ((column.colIndex === 1 || column.colIndex === 7) && (above120days+days120) > 0 && above120days <= 0) { 
        value = `<div style="background-color: #fde995; padding: 2px;">${value}</div>`;
    } else if ((column.colIndex === 1 || column.colIndex === 6) && (above120days+days120) > 0 && above120days <= 0) { 
        value = `<div style="background-color: #a6e1c5; padding: 2px;">${value}</div>`;
    }

    return value;
},



	onload: function (report) {
		report.page.add_inner_button(__("Accounts Receivable"), function () {
			var filters = report.get_values();
			frappe.set_route("query-report", "Accounts Receivable", { company: filters.company });
		});
	},
};

erpnext.utils.add_dimensions("Accounts Receivable Summary", 9);

function get_party_type_options() {
	let options = [];
	frappe.db
		.get_list("Party Type", { filters: { account_type: "Receivable" }, fields: ["name"] })
		.then((res) => {
			res.forEach((party_type) => {
				options.push(party_type.name);
			});
		});
	return options;
}