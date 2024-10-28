frappe.pages['test'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Test',
        single_column: true
    });
    new test(page);
};

test = class test {
    constructor(page) {
        this.page = page;
        this.make_form();
        this.fetch_sales_invoice_count();
	
    }

    make_form() {
        this.form = new frappe.ui.FieldGroup({
            fields: [{
                    fieldtype: "HTML",
                    fieldname: "preview",
                },
                {
                    label: __("Sales Invoice Count"),
                    fieldname: "sales_invoice_count",
                    fieldtype: "HTML",
                },


            ],
            body: this.page.body,
        });
        this.form.make();
    }

    fetch_sales_invoice_count() {
        frappe.call({
            method: "frappe.client.get_count",
            args: {
                doctype: "Sales Invoice",
		filters:{
			custom_zatca_status:'CLEARED'
			}
            },
        }).then((response) => {
            const count = response.message;

            // HTML structure for number cards and charts
            this.form.get_field("sales_invoice_count").html(`



            <div class="card-container" style="
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: space-between;
                margin-top: 20px;
            ">
                ${this.create_card("Sales Invoice Count", count)}
                ${this.create_card("Another Metric", 100)} <!-- Example additional cards -->
                ${this.create_card("Third Metric", 250)}
                ${this.create_card("Fourth Metric", 75)}
            </div>

            <!-- Chart container for two charts side by side -->
            <div style="
                margin-top: 30px; 
                display: flex;
		
                justify-content: space-between; 
                max-width: 100%;
                flex-wrap: nowrap; /* Prevent wrapping */
		
            ">
		<canvas id="salesChart" style="
		    flex: 1;
		    max-width: 49%; /* Adjust the width */
		    height: 250px; /* Set a height for the chart */
		    box-sizing: border-box;
		    border-radius: 8px; /* Rounded corners */
		    border: 1px solid #ddd; /* Light border for card effect */
		    background-color: #fff; /* Background color for card */
		    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Soft shadow for depth */
		    padding: 20px; /* Inner padding to separate content from edges */
		    margin-right: 10px;
		"></canvas>
 <!-- Chart 1 -->
                <canvas id="revenueChart" style="
                    flex: 1;
		    max-width: 49%; /* Adjust the width */
		    height: 250px; /* Set a height for the chart */
		    box-sizing: border-box;
		    border-radius: 8px; /* Rounded corners */
		    border: 1px solid #ddd; /* Light border for card effect */
		    background-color: #fff; /* Background color for card */
		    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Soft shadow for depth */
		    padding: 20px; /* Inner padding to separate content from edges */
		    margin-right: 10px;

                "></canvas> <!-- Chart 2 -->
            </div>
<div  
    style="
        flex: 1;
        margin-top: 30px;
        max-width: 100%; /* Adjust the width */
        height: 250px; /* Set a height for the chart */
        box-sizing: border-box;
        border-radius: 8px; /* Rounded corners */
        border: 1px solid #ddd; /* Light border for card effect */
        background-color: #fff; /* Background color for card */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Soft shadow for depth */
        padding: 20px; /* Inner padding to separate content from edges */
        margin-right: 10px;
        overflow-y: auto; /* Enables vertical scrolling */
        max-height: 300px; /* Set maximum height for scrolling */
    "
>
    <table class="table table-bordered table-condensed" id="task_table"></table>
</div>
        `);

            // Load Chart.js, then render the charts
            this.load_chartjs().then(() => {
                // Use setTimeout to allow rendering to stabilize
                setTimeout(() => {
                    this.render_chart("salesChart", [12, 19, 3, 5, 2, 3], 'Sales Invoices'); // Chart 1 data
                    this.render_chart("revenueChart", [5, 10, 15, 20, 25], 'Revenue', 'pie'); // Pie chart
                }, 100); // Adjust the delay if needed
            });
        });
    }

    // Helper function to create individual cards
    create_card(title, count) {
        return `
        <div class="number-card" style="
            flex: 1 1 22%;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            min-width: 100px;
        ">
            <h4 style="font-weight: bold; color: #495057;">${title}</h4>
            <div class="count" style="
                font-size: 32px;
                font-weight: bold;
                color: #007bff;
                margin-top: 10px;
            ">${count}</div>
        </div>
    `;
    }

    // Function to dynamically load Chart.js
    load_chartjs() {
        return new Promise((resolve, reject) => {
            if (typeof Chart === 'undefined') {
                const script = document.createElement('script');
                script.src = "https://cdn.jsdelivr.net/npm/chart.js";
                script.onload = resolve;
                script.onerror = (error) => {
                    console.error("Error loading Chart.js:", error);
                    reject(error);
                };
                document.head.appendChild(script);
            } else {
                resolve();
            }
        });
    }

    // Function to render the chart
    render_chart(chartId, dataValues, label, chartType = 'bar') {
        const ctx = document.getElementById(chartId).getContext('2d');

        const data = {
            labels: ['January', 'February', 'March', 'April', 'May', 'June'],
            datasets: [{
                label: label,
                data: dataValues, // Use dynamic data
                backgroundColor: chartType === 'pie' ? [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                ] : [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                ],
                borderColor: chartType === 'pie' ? [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                ] : [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                ],
                borderWidth: 1
            }]
        };

        // Chart configuration
        // Chart configuration
        new Chart(ctx, {
            type: chartType, // Use the specified chart type
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false, // Allow flexibility in height
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    fetch_and_render() {
        // set working state
        this.form.get_field("preview").html(`
            <div class="text-muted margin-top">
                ${__("Fetching...")}
            </div>
        `);
    } // Close fetch_and_render method here
};
