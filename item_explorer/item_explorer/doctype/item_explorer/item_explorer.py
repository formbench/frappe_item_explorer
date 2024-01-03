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
def get_children(parent=None, product_category=None, item_code=None, product_name=None):

	parent_object = json.loads(parent) if parent else { "value": "", "type": "" }
	parent_value = parent_object["value"]
	parent_type = parent_object["type"]
	
	child_item_filters = [["disabled", "=", 0],["variant_of", "=", parent_value]]
	parent_item_filters = [["disabled", "=", 0],["variant_of", "=", ""]]

	# Top Level
	if parent_value == "": 
		# if item code is set, this filter takes precedence
		if item_code:
			return get_items([["name", "like", item_code]])
		
		# product name filters allow for searching for multiple words
		if product_name:			
			product_name_filters = []
			categories_filters = []
			for product_name_word in product_name.split(" "):
				product_name_filters.append(["item_name", "like", "%" + product_name_word + "%"])
				categories_filters.append(["title", "like", "%" + product_name_word + "%"])

			categories = get_product_categories(categories_filters)
			items = get_items(product_name_filters)
			return categories + items
		
		# only if the two filters are empty will the hierarchy be loaded
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
			for item in variant_items:
				if item["type"] == _("Product Bundle"):
					item["type"] = _("Variant Item / Product Bundle")
				else:
					item["type"] = _("Variant Item")
			boms = get_boms([parent_value])
			return boms + variant_items # child level
		elif parent_type == _("BOM"):
			items = get_bom_items(parent_value)
			for item in items:
				item["type"] = _("BOM Item")
			return items
		elif parent_type == _("Product Bundle"):
			return get_product_bundle_items(parent_value)


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
		order_by="item_name",
	)

	# get boms for all items in filters
	# so we know if we can expand the item further
	item_names = []
	for item in items:
		item_names.append(item["name"])
	boms = get_boms(item_names)
	bundles = get_product_bundles(item_names)

	for item in items:
		item["type"] = _("Item")
		for bom in boms:
			try:
				if bom["parent"] == item["name"]:
					item["expandable"] = True
			except:
				pass

		for bundle in bundles:
			try:
				if bundle["parent"] == item["name"]:
					item["expandable"] = True
					item["type"] = _("Product Bundle")
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
		order_by="item_name",
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
	items = frappe.get_all(
		"BOM Item",
		fields=["item_code as name", "item_name as title"],
		filters=[["docstatus", "=", 1], ["parent", "=", bom]],
		order_by="item_name",
	)
	for item in items:
		item["type"] = _("Item")
		item["value"] = json.dumps({ "value": item["name"], "type": item["type"]})
	return items

def get_product_bundles(item_names):
	# construct filter for product bundles
	filters = [["disabled", "=", 0]]
	filters.append(["new_item_code", "in", item_names])
	
	bundles = frappe.get_list(
		"Product Bundle",
		fields=["name", "new_item_code as title", "new_item_code as parent"],
		filters=filters,
		order_by="new_item_code",
	)

	for bundle in bundles:

		bundle["expandable"] = True
		bundle["type"] = _("Product Bundle")
		bundle["title"] = _("Product Bundle") + " " + bundle["title"]
		bundle["value"] = json.dumps({ "value": bundle["name"], "type": bundle["type"]})

	return bundles

def get_product_bundle_items(item_name):
	bundles = get_product_bundles(item_name)
	if len(bundles) == 0:
		return []
	
	items = frappe.get_all(
		"Product Bundle Item",
		fields=["item_code as name", "description as title"],
		filters=[["parent", "=", bundles[0]["name"]]],
		order_by="item_code",
	)
	for item in items:
		item["type"] = _("Product Bundle Item")
		item["value"] = json.dumps({ "value": item["name"], "type": item["type"]})
	return items
	
def get_product_categories(filters):
	categories = frappe.get_list(
		"Product Category",
		fields=["name", "title", "parent_product_category as parent", "is_group as expandable"],
		filters=filters,
		order_by="title",
	)
	for category in categories:
		category["expandable"] = True
		category["type"] = _("Category")
		category["value"] = json.dumps({ "value": category["name"], "type": category["type"]})
	return categories