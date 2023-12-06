# Copyright (c) 2023, Erpgulf and contributors
# For license information, please see license.txt

# Copyright (c) 2023, Erpgulf and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data, chart_data = get_data_and_chart(filters)
    return columns, data, None, chart_data

def get_columns():
    return [
        "Branch:Link/Item:80",
        "Tot:Currency:100",
        "Jan:Currency:85",
        "Feb:Currency:85",
        "Mar:Currency:85",
        "Apr:Currency:85",
        "May:Currency:85",
        "Jun:Currency:85",
        "Jul:Currency:85",
        "Aug:Currency:85",
        "Sep:Currency:85",
        "Oct:Currency:85",
        "Nov:Currency:85",
        "Dec:Currency:85"      
    ]

def get_data_and_chart(filters):
    conditions = "AND 1=1 "
    if(filters.get('year')):
        conditions += f"and  year(posting_date) = '{filters.get('year')}'"
    
    query = f"""SELECT 
                    cost_center as branch,
                    SUM(if((grand_total),grand_total,0)) AS tot,
                    SUM(IF(MONTH(posting_date) = 1, grand_total, 0)) AS jan,
                    SUM(IF(MONTH(posting_date) = 2, grand_total, 0)) AS feb,
                    SUM(IF(MONTH(posting_date) = 3, grand_total, 0)) AS mar,
                    SUM(IF(MONTH(posting_date) = 4, grand_total, 0)) AS apr,
                    SUM(IF(MONTH(posting_date) = 5, grand_total, 0)) AS may,
                    SUM(IF(MONTH(posting_date) = 6, grand_total, 0)) AS jun,
                    SUM(IF(MONTH(posting_date) = 7, grand_total, 0)) AS jul,
                    SUM(IF(MONTH(posting_date) = 8, grand_total, 0)) AS aug,
                    SUM(IF(MONTH(posting_date) = 9, grand_total, 0)) AS sep,
                    SUM(IF(MONTH(posting_date) = 10, grand_total, 0)) AS oct,
                    SUM(IF(MONTH(posting_date) = 11, grand_total, 0)) AS nov,
                    SUM(IF(MONTH(posting_date) = 12, grand_total, 0)) AS `dec`
                FROM `tabSales Invoice` 
                WHERE ('1' = '1') {conditions} 
                GROUP BY cost_center"""

    data = frappe.db.sql(query, as_dict=True)

    chart_data = {'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                  'datasets': []}

    for row in data:
        branch = row['branch']
        values = [row['jan'], row['feb'], row['mar'], row['apr'], row['may'], row['jun'],
                  row['jul'], row['aug'], row['sep'], row['oct'], row['nov'], row['dec']]
        dataset = {'name': branch, 'values': values}
        chart_data['datasets'].append(dataset)

    return data, {'data': chart_data, 'type': 'bar'}
