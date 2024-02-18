function chkret(frm, dn_detail) {
    return new Promise((resolve, reject) => {
        frappe.call({
            method: "alhoda.alhoda.salessinvoice.calculate_item_quantities", 
            args: {
                item_code: dn_detail
            },
            callback: (r) => {
                if (frm.doc.is_return === 1 && r.message.result === 0) {
                    reject("Failed");
                } else {
                    resolve(r.message.result); 
                }
            }
        });
    });
}


frappe.ui.form.on('Delivery Note', {
    before_save(frm) {
        if (frm.doc.is_return === 1) {
            let promises = [];
            frm.doc.items.forEach(function (item) {
                promises.push(
                    chkret(frm, item.dn_detail).then(result => {
                        console.log(result);
                       
                    }).catch(error => {
                        frappe.validated = false; 
                        frappe.throw('Delivery Order Completed and Cannot Make Return -- >' + item.item_code)
                        return Promise.reject(); 
                    })
                );
            });

            return Promise.all(promises);
        }
    },
   
});
