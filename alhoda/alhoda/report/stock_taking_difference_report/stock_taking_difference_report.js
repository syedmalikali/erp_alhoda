frappe.query_reports["Stock Taking Difference Report"] = {
    filters: [
        {
            fieldname: "stock_taking_summary",
            label: "Stock Taking Summary",
            fieldtype: "Link",
            options: "Stock Taking Summary",
            reqd: 1
        }
    ]
};
