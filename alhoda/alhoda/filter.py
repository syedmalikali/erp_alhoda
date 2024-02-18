import frappe
# frappe.init(site="hoda-dev.erpgulf.com")
# frappe.connect()

from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.utils import unique

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_delivery_notes_to_be_billed(doctype, txt, searchfield, start, page_len, filters, as_dict):
    fields = get_fields("Delivery Note", ["name", "customer", "posting_date"])

    sql_query = (
        "SELECT " + ", ".join(["`tabDelivery Note`.{0}".format(f) for f in fields]) + 
        " FROM `tabDelivery Note`" +
        " WHERE `tabDelivery Note`.`" + searchfield + "` LIKE %(txt)s" +
        " AND `tabDelivery Note`.docstatus = 1" +
        " AND status NOT IN ('Stopped', 'Closed')" +
        " AND ((" +
        "     (`tabDelivery Note`.is_return = 0 AND `tabDelivery Note`.per_billed < 100 AND `tabDelivery Note`.per_returned != 100)" +
        "     OR (`tabDelivery Note`.grand_total = 0 AND `tabDelivery Note`.per_billed < 100)" +
        "     OR (" +
        "         `tabDelivery Note`.is_return = 1" +
        "         AND return_against IN (" +
        "             SELECT name FROM `tabDelivery Note`" +
        "             WHERE per_billed < 100 AND per_returned != 100" +
        "         )" +
        "     )" +
        " ))" + get_filters_cond(doctype, filters, []) + get_match_cond(doctype) +
        " ORDER BY `tabDelivery Note`.`" + searchfield + "` ASC" +
        " LIMIT %(page_len)s OFFSET %(start)s"
    )

    # Execute the SQL query with parameters
    query_result = frappe.db.sql(
        sql_query,
        {"txt": ("%%%s%%" % txt), "page_len": page_len, "start": start},
        as_dict=as_dict,
    )
    return query_result


def get_fields(doctype, fields=None):
    if fields is None:
        fields = []
    meta = frappe.get_meta(doctype)
    fields.extend(meta.get_search_fields())

    if meta.title_field and meta.title_field.strip() not in fields:
        fields.insert(1, meta.title_field.strip())

    return unique(fields)
