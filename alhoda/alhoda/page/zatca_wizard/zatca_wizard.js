frappe.pages['zatca-wizard'].on_page_load = function(wrapper) {
   const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Multi-Page Setup Wizard',
        single_column: true,
    });

    // Define steps (pages)
    const steps = [

{
    title: 'Step 1: Company Details',
    fields: [
    {
        fieldname: "company",
        label: __("Select Company"),
        fieldtype: "Link",
        options: "Company",
        default: frappe.defaults.get_user_default("Company"),
        reqd: 1,
        onchange: function (value) {
            // Pass the wizard instance explicitly
            handle_company_change(this, value);
        },
    },
    {
        fieldname: "company_name_display",
        label: __("Company Name Display"),
        fieldtype: "Data",
        read_only: 1, // Read-only as it will be auto-filled
    },
],
},
        {
            title: 'Step 2: Admin User',
            fields: [
                {
                    label: 'Admin Email',
                    fieldname: 'admin_email',
                    fieldtype: 'Data',
                    reqd: 1,
                },
                {
                    label: 'Admin Password',
                    fieldname: 'admin_password',
                    fieldtype: 'Password',
                    reqd: 1,
                },
            ],
        },
        {
            title: 'Step 3: Finalize',
            fields: [
                {
                    label: 'Confirm Setup',
                    fieldname: 'confirmation',
                    fieldtype: 'HTML',
                    options: '<p>All steps are completed. Click "Finish" to save your setup.</p>',
                },
            ],
        },
    ];

    // Manage the current step
    let current_step = 0;

    // Create the dialog
    const wizard = new frappe.ui.Dialog({
        title: steps[current_step].title,
        fields: steps[current_step].fields,
        primary_action_label: 'Next',
        primary_action(values) {
            if (current_step < steps.length - 1) {
                current_step++;
                update_wizard_fields();
            } else {
                // Final step: Save the setup
                frappe.call({
                    method: 'your_app.api.save_setup',
                    args: { data: values },
                    callback: function (response) {
                        frappe.msgprint(response.message || 'Setup Completed!');
                        wizard.hide();
                    },
                });
            }
        },
    });

    // Function to update the wizard fields
    function update_wizard_fields() {
        wizard.set_title(steps[current_step].title);
        wizard.fields = steps[current_step].fields;
        wizard.refresh();

        // Update the button labels
        wizard.set_primary_action(current_step === steps.length - 1 ? 'Finish' : 'Next');
        if (current_step > 0) {
            wizard.add_secondary_action('Previous', () => {
                current_step--;
                update_wizard_fields();
            });
        } else {
            wizard.secondary_action = null; // Remove "Previous" on the first step
        }
    }

    // Add a button to launch the wizard
    page.add_menu_item('Launch Wizard', () => {
        wizard.show();
    });
};
function handle_company_change(field_instance, company) {
    if (!company) return;

    // Access the wizard instance from the field
    const wizard = field_instance?.dialog;
    if (!wizard) {
        console.error("Wizard instance not found.");
        return;
    }

    // Fetch data from the Company doctype
    frappe.db.get_value("Company", company, "custom_company_registration", (r) => {
        if (r && r.custom_company_registration) {
            const display_field = wizard.get_field("company_name_display");
            if (display_field) {
                display_field.set_value(r.custom_company_registration);
            } else {
                console.error("Field 'company_name_display' not found in wizard.");
            }
        } else {
            console.log("No custom company registration found.");
        }
    });
}
