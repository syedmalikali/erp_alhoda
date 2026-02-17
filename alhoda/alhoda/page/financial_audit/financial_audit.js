frappe.pages['financial-audit'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Financial Audit',
		single_column: true
	});
}