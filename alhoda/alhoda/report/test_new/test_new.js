frappe.require("assets/erpnext/js/accounting_dimensions.js");

frappe.reportview.make({
   parent: frappe.ReportView,
   name: 'test_name',
   title: __('Test New'),
   report_name: 'test_new',
   base_report: 'erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary', // Inherit from the original
   filters: [], // Add/modify filters if needed
});