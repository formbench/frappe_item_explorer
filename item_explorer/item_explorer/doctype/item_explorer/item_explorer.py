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

	# Top Level
	if parent_value == "": 
		# if item code is set, this filter takes precedence
		if item_code:
			return get_items(list_filters=[["name", "=", item_code]])
		
		# product name filters allow for searching for multiple words
		if product_name:			
			product_name_filters = []
			categories_filters = []
			for product_name_word in product_name.split(" "):
				product_name_filters.append(["item_name", "like", "%" + product_name_word + "%"])
				categories_filters.append(["title", "like", "%" + product_name_word + "%"])

			categories = get_product_categories(categories_filters)
			items = get_items(list_filters=product_name_filters)
			return categories + items
		
		# only if the two filters are empty will the hierarchy be loaded
		return get_top_level_categories(product_category) # root level no items here since we put them in "others"
	# Virtual Category for all uncategorized items
	elif parent_value == "others": 
		items = get_items(parent_category=None) # others level
		for item in items:
			item["parent"] = "others"
		return items
	# Parent value is defined -> load children
	elif parent_value:
		if parent_type == _("Category"):
			child_categories = get_product_categories([["parent_product_category", "=", parent_value]])
			items = get_items(parent_category=parent_value)
			return child_categories + items
		elif parent_type == _("Parent Item"):
			variant_items = get_variants(parent_value)
			boms = get_boms([parent_value])
			return variant_items
		elif parent_type == _("Item") or parent_type == _("Item Variant"):
			boms = get_boms([parent_value])
			return boms
		elif parent_type == _("BOM"):
			items = get_bom_items(parent_value)
			for item in items:
				item["type"] = _("BOM Item")
			return items
		elif parent_type == _("Product Bundle") or parent_type == _("Item Variant / Product Bundle"):
			return get_product_bundle_items(parent_value)


def get_top_level_categories(category_filter):
	if(category_filter):
		categories = get_product_categories([["name", "=", category_filter]])
		return categories
	
	categories = get_product_categories([["parent_product_category", "=", ""]])
	items = get_items(parent_category=None)

	# add a top level category to catch all uncategorized items
	if (len(items)) > 0:
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

def get_items(parent_category=None, list_filters=None):
	# 
	if list_filters:
		items = frappe.get_list(
			"Item",
			fields=["name", "item_name as title", "has_variants as expandable", "variant_of as parent", "custom_product_category as product_category"],
			filters=list_filters,
			order_by="item_name",
		)
	elif parent_category:
		items = frappe.db.sql("""
			SELECT name, item_name as title, has_variants as expandable, variant_of as parent, custom_product_category as product_category
			FROM tabItem
			WHERE 
				disabled = 0 
				AND (variant_of = '' OR variant_of IS NULL) 
				AND custom_product_category = %(filter_value)s
				AND name NOT IN (
					SELECT bi.item_code FROM `tabBOM Item` bi
        			JOIN `tabBOM` b ON bi.parent = b.name
        			WHERE b.docstatus = 1
				)
		""", values={"filter_value": parent_category}, as_dict=True)
	else:
		items = frappe.db.sql("""
			SELECT name, item_name as title, has_variants as expandable, variant_of as parent, custom_product_category as product_category
			FROM tabItem
			WHERE 
				disabled = 0 
				AND (variant_of = '' OR variant_of IS NULL) 
				AND (custom_product_category = '' OR custom_product_category IS NULL)
				AND name NOT IN (
					SELECT bi.item_code FROM `tabBOM Item` bi
        			JOIN `tabBOM` b ON bi.parent = b.name
        			WHERE b.docstatus = 1
				)
		""", as_dict=True)

	# get boms for all items in filters
	# so we know if we can expand the item further
	item_names = []
	for item in items:
		item_names.append(item["name"])
	boms = get_boms(item_names)
	bundles = get_product_bundles(item_names)

	for item in items:
		item["type"] = _("Parent Item") if item["expandable"] == 1 else _("Item")
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

def get_variants(parent_item):
	# We need to duplicate the SQL query here because frappe does not allow us excessive dependency injection, only values can be passed
	items = frappe.db.sql("""
		SELECT name, item_name as title, variant_of as parent, custom_product_category as product_category
		FROM tabItem
		WHERE 
			disabled = 0 AND variant_of = %(parent_item)s
			AND name NOT IN (
				SELECT bi.item_code FROM `tabBOM Item` bi
				JOIN `tabBOM` b ON bi.parent = b.name
				WHERE b.docstatus = 1
			)
	""", values={"parent_item": parent_item}, as_dict=True)

	# get boms for all items in filters
	# so we know if we can expand the item further
	item_names = []
	for item in items:
		item_names.append(item["name"])
	boms = get_boms(item_names)
	bundles = get_product_bundles(item_names)

	for item in items:
		item["type"] = _("Item Variant")
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
					item["type"] = _("Item Variant / Product Bundle")
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
		fields=["name", "item_name as title", "item as parent", "is_default", "custom_version", "creation"],
		filters=filters,
		order_by="creation desc",
	)
	for bom in boms:
		bom["expandable"] = True
		bom["type"] = _("BOM")
		bom["title"] = _("Part List | ") + (( "v" + bom["custom_version"] + " | ") if bom["custom_version"] else " ") + bom["creation"].strftime("%Y-%m-%d")
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