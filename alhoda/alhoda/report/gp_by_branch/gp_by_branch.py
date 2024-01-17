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
        "Total Sales:Currency:100",
        "Total Cost:Currency:100",
        "Total Profit:Currency:100",
        "Jan Sales:Currency:85",
        "Jan Cost:Currency:85",
        "Jan Profit:Currency:85",
        "Feb Sales:Currency:85",
        "Feb Cost:Currency:85",
        "Feb Profit:Currency:85",
        "Mar Sales:Currency:85",
        "Mar Cost:Currency:85",
        "Mar Profit:Currency:85",
        "Apr Sales:Currency:85",
        "Apr Cost:Currency:85",
        "Apr Profit:Currency:85",
        "May Sales:Currency:85",
        "May Cost:Currency:85",
        "May Profit:Currency:85",
        "Jun Sales:Currency:85",
        "Jun Cost:Currency:85",
        "Jun Profit:Currency:85",
        "Jul Sales:Currency:85",
        "Jul Cost:Currency:85",
        "Jul Profit:Currency:85",
        "Aug Sales:Currency:85",
        "Aug Cost:Currency:85",
        "Aug Profit:Currency:85",
        "Sep Sales:Currency:85",
        "Sep Cost:Currency:85",
        "Sep Profit:Currency:85",
        "Oct Sales:Currency:85",
        "Oct Cost:Currency:85",
        "Oct Profit:Currency:85",
        "Nov Sales:Currency:85",
        "Nov Cost:Currency:85",
        "Nov Profit:Currency:85",
        "Dec Sales:Currency:85",
        "Dec Cost:Currency:85",
        "Dec Profit:Currency:85"
    ]

def get_data_and_chart(filters):
    conditions = "AND 1=1 "
    if(filters.get('year')):
        conditions += f"and  year(posting_date) = '{filters.get('year')}'"
    
    query = f"""SELECT 
                    cost_center as branch,
                    SUM(if((grand_total),grand_total,0)) AS total_sales,
                    SUM(if((grand_total),grand_total,0)) AS total_cost,
                    SUM(IF(MONTH(posting_date) = 1, grand_total, 0)) AS jan_sales,
                    SUM(IF(MONTH(posting_date) = 1, grand_total, 0)) AS jan_cost,
                    SUM(IF(MONTH(posting_date) = 2, grand_total, 0)) AS feb_sales,
                    SUM(IF(MONTH(posting_date) = 2, grand_total, 0)) AS feb_cost,
                    SUM(IF(MONTH(posting_date) = 3, grand_total, 0)) AS mar_sales,
                    SUM(IF(MONTH(posting_date) = 3, grand_total, 0)) AS mar_cost,
                    SUM(IF(MONTH(posting_date) = 4, grand_total, 0)) AS apr_sales,
                    SUM(IF(MONTH(posting_date) = 4, grand_total, 0)) AS apr_cost,
                    SUM(IF(MONTH(posting_date) = 5, grand_total, 0)) AS may_sales,
                    SUM(IF(MONTH(posting_date) = 5, grand_total, 0)) AS may_cost,
                    SUM(IF(MONTH(posting_date) = 6, grand_total, 0)) AS jun_sales,
                    SUM(IF(MONTH(posting_date) = 6, grand_total, 0)) AS jun_cost,
                    SUM(IF(MONTH(posting_date) = 7, grand_total, 0)) AS jul_sales,
                    SUM(IF(MONTH(posting_date) = 7, grand_total, 0)) AS jul_cost,
                    SUM(IF(MONTH(posting_date) = 8, grand_total, 0)) AS aug_sales,
                    SUM(IF(MONTH(posting_date) = 8, grand_total, 0)) AS aug_cost,
                    SUM(IF(MONTH(posting_date) = 9, grand_total, 0)) AS sep_sales,
                    SUM(IF(MONTH(posting_date) = 9, grand_total, 0)) AS sep_cost,
                    SUM(IF(MONTH(posting_date) = 10, grand_total, 0)) AS oct_sales,
                    SUM(IF(MONTH(posting_date) = 10, grand_total, 0)) AS oct_cost,
                    SUM(IF(MONTH(posting_date) = 11, grand_total, 0)) AS nov_sales,
                    SUM(IF(MONTH(posting_date) = 11, grand_total, 0)) AS nov_cost,
                    SUM(IF(MONTH(posting_date) = 12, grand_total, 0)) AS dec_sales,
                    SUM(IF(MONTH(posting_date) = 12, grand_total, 0)) AS dec_cost
                FROM `tabSales Invoice` 
                WHERE ('1' = '1') {conditions} 
                GROUP BY cost_center"""

    data = frappe.db.sql(query, as_dict=True)

    chart_data = {'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                  'datasets': []}

    for row in data:
        branch = row['branch']
        jan_profit = row['jan_sales'] - row['jan_cost']
        feb_profit = row['feb_sales'] - row['feb_cost']
        mar_profit = row['mar_sales'] - row['mar_cost']
        apr_profit = row['apr_sales'] - row['apr_cost']
        may_profit = row['may_sales'] - row['may_cost']
        jun_profit = row['jun_sales'] - row['jun_cost']
        jul_profit = row['jul_sales'] - row['jul_cost']
        aug_profit = row['aug_sales'] - row['aug_cost']
        sep_profit = row['sep_sales'] - row['sep_cost']
        oct_profit = row['oct_sales'] - row['oct_cost']
        nov_profit = row['nov_sales'] - row['nov_cost']
        dec_profit = row['dec_sales'] - row['dec_cost']

        values = [row['total_sales'], row['total_cost'], row['total_sales'] - row['total_cost'],
                  row['jan_sales'], row['jan_cost'], jan_profit,
                  row['feb_sales'], row['feb_cost'], feb_profit,
                  row['mar_sales'], row['mar_cost'], mar_profit,
                  row['apr_sales'], row['apr_cost'], apr_profit,
                  row['may_sales'], row['may_cost'], may_profit,
                  row['jun_sales'], row['jun_cost'], jun_profit,
                  row['jul_sales'], row['jul_cost'], jul_profit,
                  row['aug_sales'], row['aug_cost'], aug_profit,
                  row['sep_sales'], row['sep_cost'], sep_profit,
                  row['oct_sales'], row['oct_cost'], oct_profit,
                  row['nov_sales'], row['nov_cost'], nov_profit,
                  row['dec_sales'], row['dec_cost'], dec_profit]
                  
        dataset = {'name': branch, 'values': values}
        chart_data['datasets'].append(dataset)

    return data, {'data': chart_data, 'type': 'bar'}
