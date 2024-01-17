frappe.ui.form.on('Delivery Note', {
    onload: function(frm) {
        // Add a custom button to the "Create" button's dropdown menu for "Sales Return"
        frm.add_custom_button(__('Sales Return'), function() {
            // Custom action before creating Sales Return
            frappe.call({
                method: 'alhoda.alhoda.delivery.validate_returned_quantity',
                args: {
                    doc_name: frm.doc.name
                },  
                callback: function(r) {
                    if (!r.exc) {
                        // Check if the validation result is zero
                        if (r.message) {
                        }
                    }
                }
            });
        }, __("Create"));
    }
});
