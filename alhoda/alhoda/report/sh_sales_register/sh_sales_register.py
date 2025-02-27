from erpnext.accounts.report.sales_register.sales_register import execute as original_execute

def execute(filters=None):
    columns, data = original_execute(filters)
    # Remove unwanted columns
    columns = [col for col in columns if col["fieldname"] != "status"]
    print_template = """
    <html>
    <head>
        <style>
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f5f5f5; }
            .header { text-align: center; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>SH lsakdlasjSales Register</h2>
            <p>Generated on: {{ frappe.utils.format_datetime(frappe.utils.now_datetime(), "dd-MM-yyyy HH:mm") }}</p>
            {% if filters %}
                <p>Filters: {{ filters }}</p>
            {% endif %}
        </div>
        <table>
            <thead>
                <tr>
                    {% for col in columns %}
                        <th>{{ col.label }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in data %}
                    <tr>
                        {% for col in columns %}
                            <td>{{ row[col.fieldname] }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """

    return columns, data, None, print_template
