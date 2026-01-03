// Copyright (c) 2025, Syedmalikali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Taking Summary', {
    generate_summary: function (frm) {
        if (frm.is_dirty()) {
            frappe.msgprint("Please save the document before generating the summary.");
            return;
        }

        frm.call({
            doc: frm.doc,
            method: "calculate_summary",
            freeze: true,
            freeze_message: "Calculating Summary...",
            callback: function (r) {
                if (!r.exc) {
                    frm.refresh_field('items');
                }
            }
        });
    }
});
