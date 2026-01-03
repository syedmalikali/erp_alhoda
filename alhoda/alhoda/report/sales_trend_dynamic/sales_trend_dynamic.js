frappe.query_reports["Sales Trend Dynamic"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
        },

        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -11)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.get_today()
        },

        {
            "fieldname": "group_by",
            "label": __("Group By"),
            "fieldtype": "Select",
            "reqd": 1,
            "options": [
                "Territory",
                "Customer",
                "Customer Group",
                "Item",
                "Item Group",
                "Cost Center",
                "Warehouse",
                "POS Profile"
            ],
            "default": "Territory"
        }
    ],

    onload: function(report) {
        report.page.set_title(__("Sales Trend Dynamic"));
    },

    get_chart_data: function(columns, result) {
        const labels = columns.slice(1, -1).map(col => col.label);
        const datasets = result.map(row => ({
            name: row.group_name,
            values: columns.slice(1, -1).map(col => row[col.fieldname])
        }));
        return {
            data: { labels, datasets },
            type: "line",
            height: 300
        };
    }
};
