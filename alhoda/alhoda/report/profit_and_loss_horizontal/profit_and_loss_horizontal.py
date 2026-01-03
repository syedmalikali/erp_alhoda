# Copyright (c) 2025
# Custom Profit & Loss Horizontal Report (Tally Style)

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.report.financial_statements import (
    compute_growth_view_data,
    compute_margin_view_data,
    get_data,
    get_period_list,
)


def execute(filters=None):
    period_list = get_period_list(
        filters.from_fiscal_year,
        filters.to_fiscal_year,
        filters.period_start_date,
        filters.period_end_date,
        filters.filter_based_on,
        filters.periodicity,
        company=filters.company,
    )

    # Fetch Income and Expense
    income = get_data(
        filters.company,
        "Income",
        "Credit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
    )

    expense = get_data(
        filters.company,
        "Expense",
        "Debit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
    )

    # Net Profit / Loss
    net_profit_loss = get_net_profit_loss(
        income, expense, period_list, filters.company, filters.presentation_currency
    )

    # Transform into horizontal format (Tally style)
    data = []
    max_len = max(len(income), len(expense))

    for i in range(max_len):
        row = {}
        if i < len(income):
            row["income_account"] = income[i].get("account_name")
            row["income_amount"] = income[i].get("total")
        else:
            row["income_account"] = ""
            row["income_amount"] = 0

        if i < len(expense):
            row["expense_account"] = expense[i].get("account_name")
            row["expense_amount"] = expense[i].get("total")
        else:
            row["expense_account"] = ""
            row["expense_amount"] = 0

        data.append(row)

    # Add Net Profit/Loss row
    if net_profit_loss:
        total = net_profit_loss.get("total")
        data.append({
            "income_account": "Net Profit" if total > 0 else "",
            "income_amount": total if total > 0 else 0,
            "expense_account": "Net Loss" if total < 0 else "",
            "expense_amount": abs(total) if total < 0 else 0,
        })

    # Define columns (horizontal)
    columns = [
        {"label": _("Income Account"), "fieldname": "income_account", "fieldtype": "Data", "width": 200},
        {"label": _("Income Amount"), "fieldname": "income_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Expense Account"), "fieldname": "expense_account", "fieldtype": "Data", "width": 200},
        {"label": _("Expense Amount"), "fieldname": "expense_amount", "fieldtype": "Currency", "width": 150},
    ]

    # Disable chart (not useful in horizontal P&L)
    return columns, data


def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
    total_income = flt(income[-2]["total"], 3) if income else 0
    total_expense = flt(expense[-2]["total"], 3) if expense else 0
    total = total_income - total_expense

    if total != 0:
        return {
            "account_name": "Net Profit/Loss",
            "total": total,
            "currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
        }
