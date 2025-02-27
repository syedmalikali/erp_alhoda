frappe.pages['zatca-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Zatca Dashboard (ErpGulf)',
        single_column: true
    });
    new ZatcaDashboard(page);
};

class ZatcaDashboard {
    constructor(page) {
        this.page = page;
        this.initializeDashboard();
    }

    initializeDashboard() {
        this.createForm();
        this.renderStatusCards();
        this.renderCharts();
        this.renderInvoiceList();
    }

    createForm() {
        this.form = new frappe.ui.FieldGroup({
            fields: [
                { fieldtype: "HTML", fieldname: "status_cards" },
                { fieldtype: "HTML", fieldname: "zatca_charts" },
                { fieldtype: "HTML", fieldname: "invoice_list" }
            ],
            body: this.page.body
        });
        this.form.make();
    }

    renderStatusCards() {
        const statuses = ['Reported', 'Cleared', 'Cleared With Warning', 'Failed', 'Not Submitted'];
        const statusPromises = statuses.map(status => this.getCountForStatus(status));

        Promise.all(statusPromises).then(responses => {
            let cardsHtml = `<div class="status-card-container">`;
            responses.forEach((response, index) => {
                const count = response.message || 0;
                cardsHtml += this.createStatusCard(statuses[index], count);
            });
            cardsHtml += '</div>';
            this.form.get_field("status_cards").html(cardsHtml);
        });
    }

    getCountForStatus(status) {
        return frappe.call({
            method: "frappe.client.get_count",
            args: {
                doctype: "Sales Invoice",
                filters: { custom_zatca_status: status }
            }
        });
    }

    createStatusCard(title, count) {
        return `
            <div class="status-card">
                <h4>${title}</h4>
                <div class="count">${count}</div>
            </div>
        `;
    }

    renderCharts() {
        this.form.get_field("zatca_charts").html('<canvas id="zatcaChart"></canvas>');
        this.loadChartJs().then(() => {
            this.fetchMonthlyZatcaStatus();
        });
    }

    loadChartJs() {
        return new Promise((resolve, reject) => {
            if (typeof Chart !== 'undefined') {
                resolve();
                return;
            }
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    fetchMonthlyZatcaStatus() {
frappe.call({
    method: "frappe.client.get_list",
    args: {
        doctype: "Sales Invoice",
        fields: ["posting_date", "custom_zatca_status"],
        filters: {
            docstatus: 1,
            custom_zatca_status: "not submitted" // Adding the filter for custom_zatca_status
        },
        limit_page_length: 100
    },
    callback: (response) => {
        if (response.message) {
            const monthlyStatusCount = this.processZatcaStatusData(response.message);
            this.renderZatcaChart(monthlyStatusCount);
        }
    }
});

    }

    processZatcaStatusData(invoices) {
        const monthlyStatusCount = {};
        invoices.forEach(invoice => {
            const month = new Date(invoice.posting_date).getMonth();
            const status = invoice.custom_zatca_status;
            if (!monthlyStatusCount[status]) {
                monthlyStatusCount[status] = Array(12).fill(0);
            }
            monthlyStatusCount[status][month]++;
        });
        return monthlyStatusCount;
    }

    renderZatcaChart(monthlyStatusCount) {
        const ctx = document.getElementById('zatcaChart').getContext('2d');
        const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const datasets = Object.keys(monthlyStatusCount).map((status, index) => ({
            label: status,
            data: monthlyStatusCount[status],
            backgroundColor: this.getChartColor(index, 0.2),
            borderColor: this.getChartColor(index, 1),
            borderWidth: 1
        }));

        new Chart(ctx, {
            type: 'bar',
            data: { labels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { stacked: true },
                    y: { stacked: true }
                }
            }
        });
    }

    getChartColor(index, alpha) {
        const colors = [
            `rgba(255, 99, 132, ${alpha})`,
            `rgba(54, 162, 235, ${alpha})`,
            `rgba(255, 206, 86, ${alpha})`,
            `rgba(75, 192, 192, ${alpha})`,
            `rgba(153, 102, 255, ${alpha})`
        ];
        return colors[index % colors.length];
    }

    renderInvoiceList() {
        this.form.get_field("invoice_list").html('<div id="invoiceListContainer"></div>');
        this.fetchInvoices();
    }

    fetchInvoices() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Sales Invoice',
                fields: ['name', 'posting_date', 'customer_name', 'grand_total', 'custom_zatca_status'],
                filters: { custom_zatca_status: ['!=', ''] },
                limit_page_length: 20
            },
            callback: (response) => {
                if (response.message && response.message.length > 0) {
                    this.createInvoiceTable(response.message);
                } else {
                    document.getElementById("invoiceListContainer").innerHTML = "<p>No invoices available</p>";
                }
            }
        });
    }

    createInvoiceTable(invoices) {
        const tableHtml = `
	     <div class="status-card">
		
            <table class="table table-bordered table-hover">
                <caption>Sales Invoice List</caption>
                <thead class="thead-light">
                    <tr>
                        <th>Invoice Number</th>
                        <th>Date</th>
                        <th>Customer</th>
                        <th>Amount</th>
                        <th>Zatca Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${invoices.map(invoice => this.createInvoiceRow(invoice)).join('')}
                </tbody>
            </table>  </div>
        `;
        document.getElementById("invoiceListContainer").innerHTML = tableHtml;
    }

    createInvoiceRow(invoice) {
        return `
            <tr>
                <td><a href="/app/sales-invoice/${invoice.name}" target="_blank">${invoice.name}</a></td>
                <td>${frappe.datetime.str_to_user(invoice.posting_date)}</td>
                <td>${invoice.customer_name}</td>
                <td>${frappe.format(invoice.grand_total, { fieldtype: 'Currency' })}</td>
                <td><span class="badge ${this.getStatusBadgeClass(invoice.custom_zatca_status)}">${invoice.custom_zatca_status}</span></td>
            </tr>
        `;
    }

    getStatusBadgeClass(status) {
        const statusClasses = {
            'Cleared': 'badge-success',
            'Failed': 'badge-danger',
            'Reported': 'badge-info',
            'Cleared With Warning': 'badge-warning',
            'Not Submitted': 'badge-secondary'
        };
        return statusClasses[status] || 'badge-secondary';
    }
}