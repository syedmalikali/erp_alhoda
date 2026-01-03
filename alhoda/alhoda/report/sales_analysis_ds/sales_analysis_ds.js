frappe.provide("frappe.ui");
frappe.provide("frappe.query_reports");

frappe.query_reports["Sales Analysis DS"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
            "reqd": 1,
            "width": "80"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "width": "80"
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1,
            "width": "80"
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": "80"
        },
        {
            "fieldname": "group_by",
            "label": __("Group By"),
            "fieldtype": "Select",
            "options": [
                {"value": "Daily", "label": __("Daily")},
                {"value": "Weekly", "label": __("Weekly")},
                {"value": "Monthly", "label": __("Monthly")},
                {"value": "Yearly", "label": __("Yearly")},
                {"value": "Salesman", "label": __("Salesman")},
                {"value": "Cost Center", "label": __("Cost Center")},
                {"value": "Invoice", "label": __("Invoice")},
                {"value": "Item", "label": __("Item")},
                {"value": "Item Group", "label": __("Item Group")}
            ],
            "default": "Monthly",
            "width": "80"
        },
        {
            "fieldname": "salesman",
            "label": __("Salesman"),
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": "80"
        },
        {
            "fieldname": "cost_center",
            "label": __("Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": "80"
        },
        {
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": "80"
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "width": "80"
        }
    ],
    

    
    after_datatable_render: function(report) {
        // Add color coding to profit column
        const profit_col_idx = report.columns.findIndex(col => col.id === 'profit');
        if (profit_col_idx !== -1) {
            report.datatable.datamanager.columns[profit_col_idx].formatter = (row, cell, value, columnDef, dataContext) => {
                const cellNode = report.datatable.defaultFormatter(row, cell, value, columnDef, dataContext);
                if (value) {
                    cellNode.classList.add(value >= 0 ? 'profit-positive' : 'profit-negative');
                }
                return cellNode;
            };
            
            report.datatable.render();
        }
    }
};

frappe.pages['sales-analysis-df'].on_page_load = function(wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Sales Analysis DS'),
        single_column: true
    });
    
    // Initialize the report
    frappe.query_reports["Sales Analysis DS"]['onload']({
        page: wrapper,
        refresh: function() {
            frappe.query_report.refresh();
        }
    });
    
    // Load the report
    frappe.query_report = new frappe.views.QueryReport({
        parent: wrapper,
        report_name: "Sales Analysis DS"
    });
    
    frappe.query_report.refresh();
}

// Add custom CSS
const css = `
    .custom-sales-analysis-report .report-summary {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .sales-analysis-ds .summary-card {
        background: #fafbfc;
        border: 1px solid #d1d8dd;
        border-radius: 4px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .sales-analysis-ds .summary-value {
        font-size: 18px;
        font-weight: bold;
        color: #36414c;
    }
    
    .sales-analysis-ds .summary-label {
        font-size: 12px;
        color: #8d99a6;
        margin-top: 5px;
    }
    
    .sales-analysis-ds .profit-positive {
        color: #2ecc71;
    }
    
    .sales-analysis-ds .profit-negative {
        color: #e74c3c;
    }
    
    .sales-analysis-ds .chart-container {
        margin: 20px 0;
        background: white;
        border: 1px solid #d1d8dd;
        border-radius: 4px;
        padding: 15px;
    }
    
    @media (max-width: 1200px) {
        .sales-analysis-ds .report-summary {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .sales-analysis-ds .report-summary {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 480px) {
        .sales-analysis-ds .report-summary {
            grid-template-columns: 1fr;
        }
    }
`;

// Inject CSS
const style = document.createElement('style');
style.innerHTML = css;
document.head.appendChild(style);