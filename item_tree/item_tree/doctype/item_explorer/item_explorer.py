import frappe
from frappe.utils.nestedset import NestedSet
from frappe.utils import json

class ItemExplorer(NestedSet):

	def db_insert(self, *args, **kwargs):
		pass

	def load_from_db(self):
		pass

	def db_update(self, *args, **kwargs):
		pass

	@staticmethod
	def get_list(args):
		pass

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass

@frappe.whitelist()
def get_children(doctype=None, parent=None, item_code=None, warehouse_category=None, is_root=False):
	group_filters = [["item_group_name", "!=", "Alle Artikelgruppen"]]
	parent_item_filters = [["disabled", "=", 0]]
	child_item_filters = [["disabled", "=", 0]]
	is_get_items = True

	frappe.msgprint(json.dumps({"is_root": is_root, "parent": parent, "doctype": doctype}))
	# Root level
	if is_root:
		frappe.msgprint("1")
		group_filters = ([["parent_item_group", "=", "Alle Artikelgruppen"]])
		is_get_items = False
	# not root level and parent is group
	elif parent:
		frappe.msgprint("2")
		group_filters.append(["parent_item_group", "=", parent])
		parent_item_filters.append(["item_group", "=", parent])
		parent_item_filters.append(["variant_of", "=", ""])
		child_item_filters.append(["variant_of", "=", parent])
	else:
		frappe.msgprint("Unhandled Case")

	frappe.msgprint(json.dumps(group_filters))
	frappe.msgprint(json.dumps(parent_item_filters))


	collection = get_item_groups(group_filters)
	if is_get_items == True: 
		collection = collection + get_items(parent_item_filters)
		collection = collection + get_items(child_item_filters)

	return collection	


def get_items(filters):
	return frappe.get_list(
		"Item",
		fields=["name as value", "item_name as title", "has_variants as expandable", "custom_warehouse_category as warehouse_category", "variant_of as parent", "item_group"],
		filters=filters,
		order_by="name",
	)
	
def get_item_groups(filters):
	list = frappe.get_list(
		"Item Group",
		fields=["name as value", "item_group_name as title", "parent_item_group as parent", "is_group as expandable"],
		filters=filters,
		order_by="name",
	)
	for item in list:
		item["expandable"] = True
	
	return list