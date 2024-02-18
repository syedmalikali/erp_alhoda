function chkret(frm, dn_detail, qty) {
    return new Promise((resolve, reject) => {
        
        frappe.call({
            method: "alhoda.alhoda.salessinvoice.calculate_item_quantities",
            args: {
                item_code: dn_detail
            },
            callback: (r) => {
                if (!frm.doc.is_return && qty > r.message.result) {
                    reject("Failed");
                } else {
                    resolve(r.message.result);
                }
            },
            error: (err) => {
                reject(err);
            }
        });
    });
}

frappe.ui.form.on('Sales Invoice', {
    before_save(frm) {
        if (!frm.doc.is_return) {
            frm.doc.items.forEach(function(item) {
                chkret(frm, item.dn_detail, item.qty)
                    .then(result => {
                        
                    })
                    .catch(error => {
                        frappe.validated = false; 
                        frappe.throw('Delivery Order Completed and Cannot Make Return -- >' + item.item_code);
                        return Promise.reject(); 
                    });
            });
        }
    },
});
