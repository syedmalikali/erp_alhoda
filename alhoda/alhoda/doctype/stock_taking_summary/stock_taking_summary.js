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
    },

});

frappe.ui.form.on("Stock Taking Summary Item", {
    check_movement(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let f_date = frm.doc.from_date;
        let t_date = frm.doc.to_date;

        let url = `/app/query-report/Stock Ledger?item_code=${row.item_code}&warehouse=${frm.doc.warehouse}&from_date=${f_date}&to_date=${t_date}`;
        window.open(url, "_blank");
    },

 remarks(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.corrected_qty == null ) {
            return;
        }

        let diff = flt(row.corrected_qty) - flt(row.total_qty_counted);

        // no change ? do nothing
        if (diff === 0) {
            return;
        }

frappe.call({
    method: "make_adjustment_entry",  // ONLY the method name
    doc: frm.doc,                      // pass the document
    args: {
        item_code: row.item_code,
        adjustment_qty: diff
    },
    callback: function() {
        row.last_corrected_qty = row.corrected_qty;
        frm.refresh_field("items");
    }
});
    }

});
