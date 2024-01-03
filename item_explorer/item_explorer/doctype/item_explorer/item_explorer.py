import frappe
from frappe.utils.nestedset import NestedSet
from frappe.utils import json
from frappe import _

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
def get_children(parent=None, product_category=None):

	parent_object = json.loads(parent) if parent else { "value": "", "type": "" }
	parent_value = parent_object["value"]
	parent_type = parent_object["type"]
	
	child_item_filters = [["disabled", "=", 0],["variant_of", "=", parent_value]]
	parent_item_filters = [["disabled", "=", 0],["variant_of", "=", ""]]
	
	# Top Level
	if parent_value == "": 
		parent_item_filters.append(["custom_product_category", "=", ""])
		return get_top_level_categories(parent_item_filters, product_category) # root level no items here since we put them in "others"
	# Virtual Category for all uncategorized items
	elif parent_value == "others": 
		parent_item_filters.append(["custom_product_category", "=", ""])
		items = get_items(parent_item_filters) # others level
		for item in items:
			item["parent"] = "others"
		return items
	# Parent value is defined -> load children
	elif parent_value:
		if parent_type == _("Category"):
			parent_item_filters.append(["custom_product_category", "=", parent_value])
			child_categories = get_product_categories([["parent_product_category", "=", parent_value]])
			items = get_items(parent_item_filters)
			return child_categories + items
		elif parent_type == _("Item"):
			variant_items = get_items(child_item_filters)
			boms = get_boms([parent_value])
			for item in variant_items:
				item["type"] = _("Variant Item")
			return boms + variant_items # child level
		elif parent_type == _("BOM"):
			items = get_bom_items(parent_value)
			for item in items:
				item["type"] = _("BOM Item")
			return items


def get_top_level_categories(parent_item_filters, category_filter):
	if(category_filter):
		categories = get_product_categories([["name", "=", category_filter]])
		return categories
	
	categories = get_product_categories([["parent_product_category", "=", ""]])
	parent_item_filters.append(["custom_product_category", "=", ""])
	items = get_items(parent_item_filters)

	# add a top level category to catch all uncategorized items
	if len(items) > 0:
		categories.append({
			"value": json.dumps({ "value": "others", "type": _("Category") }),
			"title": _("Others"),
			"expandable": True,
			"parent": "",
			"type": _("Category")
		})
		# assign item to new parent "others"
		for item in items:
			item.parent = "others"

	return categories

def get_items(filters):
	items = frappe.get_list(
		"Item",
		fields=["name", "item_name as title", "has_variants as expandable", "variant_of as parent", "custom_product_category as product_category"],
		filters=filters,
		order_by="name",
	)

	# get boms for all items in filters
	# so we know if we can expand the item further
	item_names = []
	for item in items:
		item_names.append(item["name"])
	boms = get_boms(item_names)

	for item in items:
		item["type"] = _("Item")
		for bom in boms:
			try:
				if bom["parent"] == item["name"]:
					item["expandable"] = True
			except:
				pass
		item["value"] = json.dumps({ "value": item["name"], "type": item["type"]})
	return items

def get_boms(item_names):
	# construct filter for boms
	filters = [["docstatus", "=", 1], ["is_active", "=", 1]]
	filters.append(["item", "in", item_names])
	
	boms = frappe.get_list(
		"BOM",
		fields=["name", "item_name as title", "item as parent", "is_default"],
		filters=filters,
		order_by="name",
	)
	for bom in boms:
		bom["expandable"] = True
		bom["type"] = _("BOM")
		bom["title"] = _("Part List") + " " + bom["title"]
		if bom["is_default"] == 1:
			bom["title"] = bom["title"] +  " (" + _("Default") + ")"
		bom["value"] = json.dumps({ "value": bom["name"], "type": bom["type"]})

	return boms

def get_bom_items(bom):
	items = frappe.get_list(
		"BOM Item",
		fields=["item_code as name", "item_name as title"],
		filters=[["docstatus", "=", 1], ["parent", "=", bom]],
		order_by="name",
	)
	for item in items:
		item["type"] = _("Item")
		item["value"] = json.dumps({ "value": item["name"], "type": item["type"]})
	return items
	
def get_product_categories(filters):
	categories = frappe.get_list(
		"Product Category",
		fields=["name", "title", "parent_product_category as parent", "is_group as expandable"],
		filters=filters,
		order_by="name",
	)
	for category in categories:
		category["expandable"] = True
		category["type"] = _("Category")
		category["value"] = json.dumps({ "value": category["name"], "type": category["type"]})
	return categories