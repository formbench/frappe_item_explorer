import frappe
from frappe.utils import json

@frappe.whitelist()
def get_data(item_code):
    values = {'item_code': item_code}
    
    if item_code:
        data = frappe.db.sql("""
            SELECT
                name,
                item_name,
                has_variants,
                variant_of
            FROM
                `tabItem`
            WHERE
                variant_of = %(item_code)s OR item_code = %(item_code)s
        """, values=values, as_dict=1)
    else:
        data = frappe.db.sql("""
            SELECT
                item.name,
                item.item_name,
                item.has_variants,
                item.variant_of
            FROM
                `tabItem` item
        """, values=values, as_dict=1)

    frappe.msgprint(json.dumps(data))

    item_tree = build_tree(data)
    frappe.msgprint(json.dumps(item_tree))
    return item_tree

def build_tree(items):
    # Initialize with a default parent category
    parents = [{'item_name': 'Sonstige', 'name': 'sonstige', 'children': []}]
    parent_map = {'sonstige': 0}  # Maps item names to their index in the parents list

    # Add parents (items with variants)
    for item in items:
        if item.has_variants == 1:
            node = {'item_name': item.item_name, 'name': item.name, 'children': []}
            parents.append(node)
            parent_map[item.name] = len(parents) - 1  # Map the name to its index

    # Add children to their respective parents
    for item in items:
        node = {'item_name': item.item_name, 'name': item.name}
        parent_name = item.variant_of if item.variant_of else 'sonstige'
        
        if parent_name in parent_map:
            parent_index = parent_map[parent_name]
            parents[parent_index]['children'].append(node)

    return parents