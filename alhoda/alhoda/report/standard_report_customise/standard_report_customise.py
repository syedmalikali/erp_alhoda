# Copyright (c) 2025, Erpgulf and contributors
# For license information, please see license.txt

import frappe


from erpnext.accounts.report.general_ledger.general_ledger import validate_filters
from erpnext.accounts.report.general_ledger.general_ledger import validate_party
from erpnext.accounts.report.general_ledger.general_ledger import get_columns
from erpnext.accounts.report.general_ledger.general_ledger import set_account_currency
from erpnext.accounts.report.general_ledger.general_ledger import get_result


def execute(filters=None):
	if not filters:
		return [], []

	account_details = {}

	if filters and filters.get("print_in_account_currency") and not filters.get("account"):
		frappe.throw(_("Select an account to print in account currency"))

	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	if filters.get("party"):
		filters.party = frappe.parse_json(filters.get("party"))

	validate_filters(filters, account_details)

	validate_party(filters)

	filters = set_account_currency(filters)

	columns = get_columns(filters)

	res = get_result(filters, account_details)

	return columns, res