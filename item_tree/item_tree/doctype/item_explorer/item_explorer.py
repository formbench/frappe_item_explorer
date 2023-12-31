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
	group_filters = [["parent_product_category", "!=", "Alle Artikelgruppen"]]
	parent_item_filters = [["disabled", "=", 0],["variant_of", "=", ""]]
	child_item_filters = [["disabled", "=", 0],["variant_of", "=", parent]]

	# Root level
	if is_root: # groups without a parent, items without a category
		group_filters = ([["parent_product_category", "in", ["Alle Artikelgruppen", ""]]])
		parent_item_filters.append(["custom_product_category", "=", ""])
	elif parent == "others": # groups with a parent and items without a category
		group_filters.append(["parent_product_category", "=", parent])
		parent_item_filters.append(["custom_product_category", "=", ""])
	elif parent: # groups with a parent and items with a category
		group_filters.append(["parent_product_category", "=", parent])
		parent_item_filters.append(["custom_product_category", "=", parent])

	groups = get_item_groups(group_filters)
	items = get_items(parent_item_filters)

	# add a top level category to catch all uncategorized items
	if is_root == "true" and len(items) > 0:
		groups.append({
			"value": "others",
			"title": "Others",
			"expandable": True,
			"parent": "",
		})
		# assign item to new parent "others"
		for item in items:
			item.parent = "others"

	collection = []
	for item in items:
		item["type"] = "Item"
	for group in groups:
		group["type"] = "Group"

	if parent == "others":
		collection = items # others level
	elif parent:
		variant_items = get_items(child_item_filters)
		for item in variant_items:
			item["type"] = "Variant Item"
		collection = groups + items + variant_items # child level
	else:
		collection = groups # root level no items here since we put them in "others"

	return collection


def get_items(filters):
	return frappe.get_list(
		"Item",
		fields=["name as value", "item_name as title", "has_variants as expandable", "custom_warehouse_category as warehouse_category", "variant_of as parent", "custom_product_category as product_category"],
		filters=filters,
		order_by="name",
	)
	
def get_item_groups(filters):
	list = frappe.get_list(
		"Product Category",
		fields=["name as value", "title", "parent_product_category as parent", "is_group as expandable"],
		filters=filters,
		order_by="name",
	)
	for group in list:
		group["expandable"] = True
	
	return list