// File 2: daily_sales_purchase_expense_analysis.js
// Place this in: dynamic_report_builder/alhoda/report/daily_sales_purchase_expense_analysis/

frappe.query_reports["Daily Sales Purchase Expense Analysis"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
            "reqd": 1,
            "width": "80px"
        },
        {
            "fieldname": "to_date", 
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "width": "80px"
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1,
            "width": "100px"
        },
        {
            "fieldname": "cost_center",
            "label": __("Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": "100px"
        },
        {
            "fieldname": "view_type",
            "label": __("View Type"),
            "fieldtype": "Select",
            "options": "Daily\nWeekly\nMonthly",
            "default": "Daily",
            "width": "80px"
        }
    ],

    onload: function(report) {
        // Add custom buttons to report toolbar
        report.page.add_inner_button(__("Export Dashboard"), function() {
            export_dashboard_data(report);
        });

        report.page.add_inner_button(__("Email Report"), function() {
            email_report(report);
        });

        report.page.add_inner_button(__("Download PDF"), function() {
            download_pdf_report(report);
        });

        report.page.add_inner_button(__("Advanced Analytics"), function() {
            show_advanced_analytics(report);
        });

        // Add custom CSS for better visualization
        add_custom_styles();
        
        // Initialize additional charts
        setTimeout(() => {
            load_additional_charts(report);
        }, 1000);
    },

    after_datatable_render: function(datatable_obj) {
        // Add conditional formatting to data table
        apply_conditional_formatting(datatable_obj);
        
        // Add click handlers for drill-down
        add_drill_down_handlers(datatable_obj);
    },

    formatter: function(value, row, column, data, default_formatter) {
        // Custom formatting for specific columns
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname === "net_amount") {
            if (flt(value) < 0) {
                value = `<span style="color: red; font-weight: bold;">${value}</span>`;
            } else if (flt(value) > 0) {
                value = `<span style="color: green; font-weight: bold;">${value}</span>`;
            }
        }
        
        if (column.fieldname === "profit_margin") {
            // Fix: Use the actual value, not row[column.fieldname]
            const margin = flt(value);
            if (margin < 0) {
                value = `<span style="color: red;">${value}</span>`;
            } else if (margin > 20) {
                value = `<span style="color: green; font-weight: bold;">${value}</span>`;
            } else if (margin > 10) {
                value = `<span style="color: orange;">${value}</span>`;
            }
        }
        
        return value;
    },

    get_datatable_options: function(options) {
        // Customize datatable options
        return Object.assign(options, {
            checkboxColumn: true,
            inlineFilters: true,
            layout: "fluid",
            noDataMessage: __("No data found for the selected period"),
            cellHeight: 35,
            dynamicRowHeight: true
        });
    }
};

function add_custom_styles() {
    // Remove existing styles first
    $('#daily-analysis-styles').remove();
    
    const custom_css = `
        <style id="daily-analysis-styles">
            /* Weekend highlighting */
            .report-wrapper table tbody tr:has(td:nth-child(2):contains('Saturday')),
            .report-wrapper table tbody tr:has(td:nth-child(2):contains('Sunday')) {
                background-color: #f8f9fa !important;
            }
            
            /* Positive/Negative value styling */
            .report-wrapper table tbody td[data-fieldname="net_amount"] {
                font-weight: bold !important;
            }
            
            .report-wrapper table tbody td[data-fieldname="profit_margin"] {
                font-weight: bold !important;
            }
            
            /* Chart container styling */
            .report-wrapper .chart-container {
                background: white !important;
                border-radius: 8px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                margin-bottom: 20px !important;
                padding: 15px !important;
            }
            
            /* Summary cards */
            .summary-cards {
                display: flex !important;
                flex-wrap: wrap !important;
                gap: 15px !important;
                margin: 20px 0 !important;
            }
            
            .summary-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                padding: 20px !important;
                border-radius: 10px !important;
                flex: 1 !important;
                min-width: 200px !important;
                text-align: center !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
            }
            
            .summary-card h3 {
                margin: 0 0 10px 0 !important;
                font-size: 2em !important;
            }
            
            .summary-card p {
                margin: 0 !important;
                opacity: 0.9 !important;
            }
            
            /* Analytics dashboard */
            .analytics-dashboard {
                display: grid !important;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)) !important;
                gap: 20px !important;
                margin: 20px 0 !important;
            }
            
            .chart-widget {
                background: white !important;
                border: 1px solid #e0e6ed !important;
                border-radius: 8px !important;
                padding: 15px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
            }
            
            .chart-widget h4 {
                margin: 0 0 15px 0 !important;
                color: #333 !important;
                border-bottom: 2px solid #f0f0f0 !important;
                padding-bottom: 10px !important;
            }
            
            /* Table styling improvements */
            .report-wrapper .datatable .data-table-wrapper {
                border-radius: 8px !important;
                overflow: hidden !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
            }
            
            .report-wrapper .datatable .data-table-header {
                background: #f8f9fa !important;
                font-weight: bold !important;
            }
            
            /* Clickable cells */
            .clickable-cell {
                cursor: pointer !important;
                text-decoration: underline !important;
                color: #007bff !important;
            }
            
            .clickable-cell:hover {
                background-color: #e3f2fd !important;
            }
            
            /* Value styling classes */
            .positive-value { 
                color: #28a745 !important; 
                font-weight: bold !important; 
            }
            
            .negative-value { 
                color: #dc3545 !important; 
                font-weight: bold !important; 
            }
            
            .neutral-value { 
                color: #6c757d !important; 
            }
            
            /* Trend indicators */
            .trend-up::after { 
                content: " ?" !important; 
                color: #28a745 !important; 
                font-weight: bold !important;
            }
            
            .trend-down::after { 
                content: " ?" !important; 
                color: #dc3545 !important; 
                font-weight: bold !important;
            }
            
            .trend-stable::after { 
                content: " ?" !important; 
                color: #6c757d !important; 
            }
            
            /* Insights panel */
            .insights-panel {
                padding: 15px !important;
                background: #f8f9fa !important;
                border-radius: 8px !important;
                border: 1px solid #e0e6ed !important;
            }
            
            .insight-item {
                margin: 10px 0 !important;
                padding: 12px !important;
                background: white !important;
                border-left: 4px solid #007bff !important;
                border-radius: 4px !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            }
            
            .insight-item.warning {
                border-left-color: #ffc107 !important;
                background: #fff9e6 !important;
            }
            
            .insight-item.success {
                border-left-color: #28a745 !important;
                background: #e8f5e8 !important;
            }
            
            .insight-item.danger {
                border-left-color: #dc3545 !important;
                background: #ffe6e6 !important;
            }
            
            /* High performance row highlighting */
            .high-performance {
                border-left: 4px solid #28a745 !important;
                background-color: #f8fff8 !important;
            }
            
            .low-performance {
                border-left: 4px solid #dc3545 !important;
                background-color: #fff8f8 !important;
            }
            
            /* Print styles */
            @media print {
                .summary-cards { 
                    flex-direction: column !important; 
                }
                .analytics-dashboard { 
                    grid-template-columns: 1fr !important; 
                }
                .chart-widget {
                    break-inside: avoid !important;
                }
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .analytics-dashboard {
                    grid-template-columns: 1fr !important;
                }
                .summary-card {
                    min-width: 100% !important;
                }
            }
        </style>
    `;
    
    // Force add to head
    $('head').append(custom_css);
    
    // Also add to document body for fallback
    if (!$('body').find('#daily-analysis-styles-fallback').length) {
        $('body').append(`<div id="daily-analysis-styles-fallback">${custom_css}</div>`);
    }
}

function apply_conditional_formatting(datatable_obj) {
    // Apply conditional formatting to specific rows and cells
    if (!datatable_obj || !datatable_obj.bodyRenderer) return;
    
    setTimeout(() => {
        // First apply custom styles
        add_custom_styles();
        
        // Get all rows from the datatable
        const tableRows = $('.report-wrapper table tbody tr');
        
        tableRows.each(function(index) {
            const $row = $(this);
            const cells = $row.find('td');
            
            if (cells.length === 0) return;
            
            // Get day name (2nd column, index 1)
            const dayName = cells.eq(1).text().trim();
            
            // Highlight weekends
            if (dayName === 'Saturday' || dayName === 'Sunday') {
                $row.css({
                    'background-color': '#f8f9fa !important',
                    'border-left': '3px solid #6c757d'
                });
            }
            
            // Get net amount (9th column, index 8)
            const netAmountCell = cells.eq(8);
            const netAmountText = netAmountCell.text().replace(/[^\d.-]/g, '');
            const netAmount = parseFloat(netAmountText) || 0;
            
            // Format net amount
            if (netAmount > 0) {
                netAmountCell.addClass('positive-value').css({
                    'color': '#28a745 !important',
                    'font-weight': 'bold !important'
                });
            } else if (netAmount < 0) {
                netAmountCell.addClass('negative-value').css({
                    'color': '#dc3545 !important',
                    'font-weight': 'bold !important'
                });
            } else {
                netAmountCell.addClass('neutral-value').css({
                    'color': '#6c757d !important'
                });
            }
            
            // Get profit margin (10th column, index 9)
            const profitMarginCell = cells.eq(9);
            const profitMarginText = profitMarginCell.text().replace(/[^\d.-]/g, '');
            const profitMargin = parseFloat(profitMarginText) || 0;
            
            // Format profit margin
            if (profitMargin < 0) {
                profitMarginCell.css({
                    'color': '#dc3545 !important',
                    'font-weight': 'bold !important'
                });
            } else if (profitMargin > 20) {
                profitMarginCell.css({
                    'color': '#28a745 !important',
                    'font-weight': 'bold !important'
                });
            } else if (profitMargin > 10) {
                profitMarginCell.css({
                    'color': '#ff8c00 !important',
                    'font-weight': 'bold !important'
                });
            }
            
            // Get sales amount (3rd column, index 2) for performance highlighting
            const salesAmountText = cells.eq(2).text().replace(/[^\d.-]/g, '');
            const salesAmount = parseFloat(salesAmountText) || 0;
            
            // Calculate average for comparison (simplified)
            const avgSales = get_table_average_sales();
            
            if (salesAmount > avgSales * 1.2) {
                $row.css({
                    'border-left': '4px solid #28a745',
                    'background-color': '#f8fff8'
                }).addClass('high-performance');
            } else if (salesAmount > 0 && salesAmount < avgSales * 0.8) {
                $row.css({
                    'border-left': '4px solid #dc3545',
                    'background-color': '#fff8f8'
                }).addClass('low-performance');
            }
        });
        
        // Apply clickable styling to amount columns
        add_clickable_styling();
        
    }, 200);
}

function get_table_average_sales() {
    // Calculate average sales from visible table data
    let total = 0;
    let count = 0;
    
    $('.report-wrapper table tbody tr').each(function() {
        const salesCell = $(this).find('td').eq(2);
        const salesText = salesCell.text().replace(/[^\d.-]/g, '');
        const salesAmount = parseFloat(salesText) || 0;
        
        if (salesAmount > 0) {
            total += salesAmount;
            count++;
        }
    });
    
    return count > 0 ? total / count : 0;
}

function add_clickable_styling() {
    // Add clickable styling to sales, purchase, and expense amount columns
    $('.report-wrapper table tbody tr').each(function() {
        const $row = $(this);
        
        // Sales Amount (column 3)
        const salesCell = $row.find('td').eq(2);
        salesCell.addClass('clickable-cell').css({
            'cursor': 'pointer',
            'text-decoration': 'underline',
            'color': '#007bff !important'
        });
        
        // Purchase Amount (column 5)
        const purchaseCell = $row.find('td').eq(4);
        purchaseCell.addClass('clickable-cell').css({
            'cursor': 'pointer',
            'text-decoration': 'underline',
            'color': '#007bff !important'
        });
        
        // Expense Amount (column 7)
        const expenseCell = $row.find('td').eq(6);
        expenseCell.addClass('clickable-cell').css({
            'cursor': 'pointer',
            'text-decoration': 'underline',
            'color': '#007bff !important'
        });
    });
}

function get_average_sales(datatable_obj) {
    const data = datatable_obj.datamanager.data || [];
    const total = data.reduce((sum, row) => sum + flt(row[2]), 0); // sales_amount
    return total / data.length;
}

function add_drill_down_handlers(datatable_obj) {
    // Add click handlers for drill-down functionality using jQuery
    setTimeout(() => {
        // Remove existing handlers
        $('.report-wrapper table tbody tr td').off('click.drill-down');
        
        // Add click handlers to amount columns
        $('.report-wrapper table tbody tr').each(function(rowIndex) {
            const $row = $(this);
            const cells = $row.find('td');
            
            if (cells.length === 0) return;
            
            // Get the date from first column for drill-down
            const dateText = cells.eq(0).text().trim();
            
            // Sales Amount (column 3, index 2)
            cells.eq(2).on('click.drill-down', function(e) {
                e.preventDefault();
                drill_down_to_details('sales_amount', dateText, $row);
            });
            
            // Purchase Amount (column 5, index 4)  
            cells.eq(4).on('click.drill-down', function(e) {
                e.preventDefault();
                drill_down_to_details('purchase_amount', dateText, $row);
            });
            
            // Expense Amount (column 7, index 6)
            cells.eq(6).on('click.drill-down', function(e) {
                e.preventDefault();
                drill_down_to_details('expense_amount', dateText, $row);
            });
        });
        
        // Add hover effects
        $('.clickable-cell').hover(
            function() {
                $(this).css('background-color', '#e3f2fd');
            },
            function() {
                $(this).css('background-color', '');
            }
        );
        
    }, 300);
}

function drill_down_to_details(type, dateText, $row) {
    const doctype_map = {
        'sales_amount': 'Sales Invoice',
        'purchase_amount': 'Purchase Invoice', 
        'expense_amount': 'Expense Claim'
    };
    
    const doctype = doctype_map[type];
    if (!doctype) return;
    
    // Convert date text to proper format if needed
    let filterDate = dateText;
    
    // Handle different date formats
    if (dateText.includes('-')) {
        // Already in YYYY-MM-DD format
        filterDate = dateText;
    } else {
        // Try to parse and format the date
        try {
            const parsedDate = frappe.datetime.str_to_obj(dateText);
            filterDate = frappe.datetime.obj_to_str(parsedDate);
        } catch (e) {
            filterDate = dateText;
        }
    }
    
    // Set route options for filtered list view
    frappe.route_options = {
        'posting_date': filterDate,
        'docstatus': 1
    };
    
    // Show a message to user
    frappe.show_alert({
        message: `Opening ${doctype} list for ${dateText}`,
        indicator: 'blue'
    });
    
    // Navigate to filtered list
    frappe.set_route('List', doctype);
}

function load_additional_charts(report) {
    const filters = report.get_filter_values();
    
    frappe.call({
        method: "alhoda.alhoda.report.daily_sales_purchase_expense_analysis.daily_sales_purchase_expense_analysis.get_additional_charts",
        args: { filters: filters },
        callback: function(r) {
            if (r.message) {
                render_additional_analytics(r.message, report);
            }
        }
    });
}

function render_additional_analytics(data, report) {
    // Create analytics dashboard container
    let dashboard_html = `
        <div class="analytics-dashboard">
            <div class="chart-widget">
                <h4>Weekly Performance Trend</h4>
                <div id="weekly-chart"></div>
            </div>
            <div class="chart-widget">
                <h4>Day-wise Average Performance</h4>
                <div id="day-chart"></div>
            </div>
            <div class="chart-widget">
                <h4>Expense Breakdown</h4>
                <div id="expense-chart"></div>
            </div>
            <div class="chart-widget">
                <h4>Quick Insights</h4>
                <div class="insights-panel"></div>
            </div>
        </div>
    `;
    
    // Add dashboard to report wrapper
    if (!$('.analytics-dashboard').length) {
        $('.report-wrapper .page-form').after(dashboard_html);
    }
    
    // Render weekly trend chart
    if (data.weekly_trend && data.weekly_trend.length > 0) {
        render_weekly_chart(data.weekly_trend);
    }
    
    // Render day-wise average chart
    if (data.day_wise_avg && data.day_wise_avg.length > 0) {
        render_day_wise_chart(data.day_wise_avg);
    }
    
    // Render expense breakdown chart
    if (data.expense_breakdown && data.expense_breakdown.length > 0) {
        render_expense_breakdown_chart(data.expense_breakdown);
    }
    
    // Generate insights
    if (data.insights) {
        render_insights(data.insights);
    }
}

function render_weekly_chart(data) {
    const chart = new frappe.Chart("#weekly-chart", {
        title: "Weekly Performance",
        data: {
            labels: data.map(d => d.week),
            datasets: [
                {
                    name: "Sales",
                    values: data.map(d => d.sales),
                    chartType: 'line'
                },
                {
                    name: "Purchase",
                    values: data.map(d => d.purchase),
                    chartType: 'line'
                },
                {
                    name: "Expense",
                    values: data.map(d => d.expense),
                    chartType: 'line'
                }
            ]
        },
        type: 'axis-mixed',
        height: 300,
        colors: ['#28a745', '#dc3545', '#ffc107'],
        axisOptions: {
            xAxisMode: 'tick',
            xIsSeries: true
        }
    });
}

function render_day_wise_chart(data) {
    const chart = new frappe.Chart("#day-chart", {
        title: "Average Performance by Day",
        data: {
            labels: data.map(d => d.day_name),
            datasets: [
                {
                    name: "Avg Sales",
                    values: data.map(d => d.avg_sales)
                }
            ]
        },
        type: 'bar',
        height: 300,
        colors: ['#007bff'],
        barOptions: {
            spaceRatio: 0.5
        }
    });
}

function render_expense_breakdown_chart(data) {
    const chart = new frappe.Chart("#expense-chart", {
        title: "Expense Categories",
        data: {
            labels: data.map(d => d.category),
            datasets: [
                {
                    name: "Amount",
                    values: data.map(d => d.amount)
                }
            ]
        },
        type: 'pie',
        height: 300,
        colors: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
    });
}

function render_insights(insights) {
    let insights_html = '';
    
    insights.forEach(insight => {
        const type = insight.type || 'info';
        insights_html += `
            <div class="insight-item ${type}">
                <strong>${insight.title}</strong><br>
                ${insight.description}
            </div>
        `;
    });
    
    $('.insights-panel').html(insights_html);
}

function export_dashboard_data(report) {
    const filters = report.get_filter_values();
    
    frappe.call({
        method: "alhoda.alhoda.report.daily_sales_purchase_expense_analysis.daily_sales_purchase_expense_analysis.export_dashboard_data",
        args: { filters: filters },
        callback: function(r) {
            if (r.message && r.message.file_url) {
                window.open(r.message.file_url, '_blank');
                frappe.msgprint(__("Dashboard data exported successfully"));
            }
        }
    });
}

function email_report(report) {
    const filters = report.get_filter_values();
    
    frappe.prompt([
        {
            fieldname: 'recipients',
            label: __('Recipients'),
            fieldtype: 'Small Text',
            reqd: 1,
            description: __('Enter email addresses separated by commas')
        },
        {
            fieldname: 'subject',
            label: __('Subject'),
            fieldtype: 'Data',
            default: `Daily Sales Purchase Expense Analysis - ${frappe.datetime.str_to_user(filters.from_date)} to ${frappe.datetime.str_to_user(filters.to_date)}`,
            reqd: 1
        },
        {
            fieldname: 'message',
            label: __('Message'),
            fieldtype: 'Small Text',
            default: 'Please find attached the daily sales, purchase and expense analysis report.'
        }
    ], function(values) {
        frappe.call({
            method: "alhoda.alhoda.report.daily_sales_purchase_expense_analysis.daily_sales_purchase_expense_analysis.email_report",
            args: {
                filters: filters,
                recipients: values.recipients,
                subject: values.subject,
                message: values.message
            },
            callback: function(r) {
                if (r.message) {
                    frappe.msgprint(__("Report emailed successfully"));
                }
            }
        });
    }, __('Email Report'), __('Send'));
}

function download_pdf_report(report) {
    const filters = report.get_filter_values();
    
    frappe.call({
        method: "alhoda.alhoda.report.daily_sales_purchase_expense_analysis.daily_sales_purchase_expense_analysis.generate_pdf_report",
        args: { filters: filters },
        callback: function(r) {
            if (r.message && r.message.file_url) {
                window.open(r.message.file_url, '_blank');
                frappe.msgprint(__("PDF report generated successfully"));
            }
        }
    });
}

function show_advanced_analytics(report) {
    const filters = report.get_filter_values();
    
    // Create advanced analytics dialog
    const dialog = new frappe.ui.Dialog({
        title: __('Advanced Analytics'),
        size: 'extra-large',
        fields: [
            {
                fieldname: 'analytics_content',
                fieldtype: 'HTML',
                options: '<div id="advanced-analytics-container" style="height: 600px;">Loading...</div>'
            }
        ]
    });
    
    dialog.show();
    
    frappe.call({
        method: "alhoda.alhoda.report.daily_sales_purchase_expense_analysis.daily_sales_purchase_expense_analysis.get_advanced_analytics",
        args: { filters: filters },
        callback: function(r) {
            if (r.message) {
                render_advanced_analytics(r.message, dialog);
            }
        }
    });
}

function render_advanced_analytics(data, dialog) {
    let analytics_html = `
        <div class="advanced-analytics-dashboard">
            <div class="row">
                <div class="col-md-6">
                    <div class="chart-widget">
                        <h5>Sales Trend Analysis</h5>
                        <div id="adv-sales-trend"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-widget">
                        <h5>Profit Margin Trend</h5>
                        <div id="adv-profit-trend"></div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <div class="chart-widget">
                        <h5>Comparative Analysis</h5>
                        <div id="adv-comparative"></div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <div class="insights-summary">
                        <h5>Key Performance Indicators</h5>
                        <div id="kpi-summary"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    dialog.fields_dict.analytics_content.$wrapper.html(analytics_html);
    
    // Render advanced charts
    setTimeout(() => {
        if (data.sales_trend) {
            render_advanced_sales_trend(data.sales_trend);
        }
        if (data.profit_trend) {
            render_profit_trend(data.profit_trend);
        }
        if (data.comparative_data) {
            render_comparative_chart(data.comparative_data);
        }
        if (data.kpis) {
            render_kpi_summary(data.kpis);
        }
    }, 500);
}

function render_advanced_sales_trend(data) {
    const chart = new frappe.Chart("#adv-sales-trend", {
        title: "Sales Trend with Moving Average",
        data: {
            labels: data.map(d => d.date),
            datasets: [
                {
                    name: "Daily Sales",
                    values: data.map(d => d.sales),
                    chartType: 'bar'
                },
                {
                    name: "7-Day Moving Avg",
                    values: data.map(d => d.moving_avg),
                    chartType: 'line'
                }
            ]
        },
        type: 'axis-mixed',
        height: 250,
        colors: ['#36A2EB', '#FF6384']
    });
}

function render_profit_trend(data) {
    const chart = new frappe.Chart("#adv-profit-trend", {
        title: "Profit Margin %",
        data: {
            labels: data.map(d => d.date),
            datasets: [
                {
                    name: "Profit Margin %",
                    values: data.map(d => d.margin)
                }
            ]
        },
        type: 'line',
        height: 250,
        colors: ['#4BC0C0'],
        lineOptions: {
            regionFill: 1
        }
    });
}

function render_comparative_chart(data) {
    const chart = new frappe.Chart("#adv-comparative", {
        title: "Period over Period Comparison",
        data: {
            labels: data.map(d => d.period),
            datasets: [
                {
                    name: "Current Period",
                    values: data.map(d => d.current)
                },
                {
                    name: "Previous Period",
                    values: data.map(d => d.previous)
                }
            ]
        },
        type: 'bar',
        height: 250,
        colors: ['#28a745', '#dc3545'],
        barOptions: {
            spaceRatio: 0.3
        }
    });
}

function render_kpi_summary(kpis) {
    let kpi_html = '<div class="row">';
    
    kpis.forEach(kpi => {
        const trend_class = kpi.trend === 'up' ? 'trend-up' : kpi.trend === 'down' ? 'trend-down' : 'trend-stable';
        
        kpi_html += `
            <div class="col-md-3">
                <div class="kpi-card text-center p-3 mb-3" style="border: 1px solid #e0e6ed; border-radius: 8px;">
                    <h6 class="text-muted">${kpi.title}</h6>
                    <h4 class="${trend_class}">${kpi.value}</h4>
                    <small class="text-muted">${kpi.description}</small>
                </div>
            </div>
        `;
    });
    
    kpi_html += '</div>';
    $('#kpi-summary').html(kpi_html);
}