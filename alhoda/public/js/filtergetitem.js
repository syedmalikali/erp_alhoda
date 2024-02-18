frappe.ui.form.on('Sales Invoice', {
    onload: function(frm) {
        delivery_note_btn(frm);
    }
});

function delivery_note_btn(frm) {
    frm.add_custom_button(__('Delivery Note'), function() {
        erpnext.utils.map_current_doc({
            method: "erpnext.stock.doctype.delivery_note.delivery_note.make_sales_invoice",
            source_doctype: "Delivery Note",
            target: frm,
            date_field: "posting_date",
            setters: {
                customer: frm.doc.customer || undefined
            },
            get_query: function() {
                var filters = {
                    docstatus: 1,
                    company: frm.doc.company,
                    is_return: 0
                };
                if (frm.doc.customer) filters["customer"] = frm.doc.customer;
                return {
                    query: "alhoda.alhoda.filter.get_delivery_notes_to_be_billed",
                    filters: filters
                };
            }
        });
    }, __("Get Items From"));
}
